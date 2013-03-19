#! /usr/local/bin/python
import os, sys, string,array,struct
from numpy import *
#from scipy.io import npfile
class VIRTISpy:
  """
	PDS data reader for VIRTIS (Visible and Infrared Thermal Imaging Spectrometer) on board of the mission Venus Express
	"""
	def __init__(self,fn=''):
		self._Channel=''
		self._dataType=''
		self._header=[]
		self._qube=[]
		self._dim = [] 
		self._scet=[]
		self._table=[]
		self._geoCoeff=[]
		self._geoName=[]
		self._HK=[]
		self._HKName=[]
		if fn != '':
			self.readPDSFile(fn)
				
	def reduceHeader(self,header):
		"""
		Internal function. check if the keyword values were writed in many lines and correct the output array
		"""
		fl=0
		for i in range(len(header)):
			if len(header[i])>2:
				if (header[i][2][0] == '{' and header[i][-1][-1] !='}'):
					header[i].extend(header[i+1])
					del header[i+1]
					fl=1
					break
				if (header[i][2][0] == '(' and header[i][-1][-1] !=')'):
					header[i].extend(header[i+1])
					del header[i+1]
					fl=1
					break
		if fl == 1:
			header=self.reduceHeader(header)
		return header
			
	def readHeader(self,fn):
		"""
		Internal function. Read the input file and extract the PDS header
		"""
		header=[]
		in_file = open(fn,"rb")
		in_file.seek(0,2)
		if in_file.tell() == 0: # Empty file
			return
		else:
			in_file.seek(0)
		while 1:
			line = in_file.readline().split()
			if len(line) == 1 and line[0] == 'END': # End of header
				break
			if not line: # Empty line
				continue
			if line[0] == '/*': # Comment
				continue
			header.append(line)
		in_file.close()
		header=self.reduceHeader(header)
		for i in range(len(header)):
			if len(header[i]) >3 and header[i][1] == '=':
				header[i][2]=' '.join(header[i][2:])
				del header[i][3:]
		return header

	def headerValue(self,key):
		for line in self._header:
			if line[0] == key:
				return line[2]

	def getBand(self,band):
		if band > self._dim[0]:
			print 'Error, band value is out of range. The max value is %s'%(self._dim[0])
			sys.exit()
		else:
			if self._dataType == 'VIRTIS DATA':
				ret= transpose(self._qube[band,:,:])
			elif self._dataType== 'VIRTIS GEOMETRY':
				ret= transpose(self._qube[band,:,:]*self._geoCoeff[band])
			return ret

	def getGeometry(self,plane):
		if type(plane).__name__ == 'str':
			if plane in self._geoName:
				#print self._geoName.index(plane)
				return self.getBand(self._geoName.index(plane))
			else:
				print plane+' is not a valid geometric plane'
				sys.exit()
		else:
			return self.getBand(plane)

	def getSpectrum(self,sample,line):
		if sample >= self._dim[1]:
			print 'Error, sample value is out of range. The max value is %s'%(self._dim[1]-1)
			sys.exit()
		if line >= self._dim[2]:
			print 'Error, line value is out of range. The max value is %s'%(self._dim[2]-1)
			sys.exit()
		ret=self._qube[:,sample,line]
		return ret

	def getWave(self):
		return self._table[:,0,0]
	
	def getSCET(self,line):
		scet=list(self._HK[0:3,0,line])
		return scet
	def getHK(self,val,line):
		if type(val).__name__=='str':
			if val in self._HKName:
				idx=self._HKName.index(val)
			else:
				print val+' is not a valid Housekiping record'
				sys.exit()
		else:
			if val < len(self._HKName):
				idx=val
			else:
				print 'Not valid Housekiping record >0 <%d'%(len(self._HKName))
				sys.exit()
		if type(line).__name__== 'list':
			ret=[]
			for i in line:
				ret.append(self._HK[idx,0,i])
		else:
			ret=self._HK[idx,0, line]
		return ret
	def readPDSFile(self,fn):
		"""
		Data reader
		Supported Formats:
			-- VIRTIS M IR Raw
			-- VIRTIS M IR Calibrated
			-- VIRTIS M IR Geometry
		
		"""
		self._header=self.readHeader(fn)
		self._Channel=self.headerValue('VEX:CHANNEL_ID')[1:-1]
		recByte=int(self.headerValue('RECORD_BYTES'))
		qubPos=int(self.headerValue('^QUBE'))
		dataPos=qubPos -1
		fl=open(fn,'rb')
		fl.seek(dataPos*recByte)
		core=self.headerValue('CORE_ITEMS')[1:-1].split(',')
		crType=self.headerValue('CORE_ITEM_TYPE')
		sfxItem=self.headerValue('SUFFIX_ITEMS')[1:-1].split(',')
		self._dim=[int(core[0]),int(core[1]),int(core[2])]
		if crType == '"REAL"':
			tp='f'
			crByte=4
		elif crType == 'MSB_INTEGER':
			crByte=int(self.headerValue('CORE_ITEM_BYTES'))
			if crByte ==4:
				tp='i'
			elif crByte == 2:
				tp='h'
		coreBlock=(self._dim[0]+int(sfxItem[0]))*(self._dim[1]+int(sfxItem[1]))*self._dim[2]*crByte
		buff=fl.read()
		shape=(self._dim[0]+int(sfxItem[0]),(self._dim[1]+int(sfxItem[1])),self._dim[2])
		lineDim=self._dim[2]*crByte
		suffElem=int(sfxItem[0])*'L'
		dataStruc=str(self._dim[0])+tp+suffElem
		d=(self._dim[1]+int(sfxItem[1]))*self._dim[2]*dataStruc
		out=struct.unpack_from('>'+d,buff)
		self._dataType=self.headerValue('STANDARD_DATA_PRODUCT_ID')[1:-1]
		if self._dataType == 'VIRTIS DATA':
			procLev=int(self.headerValue('PROCESSING_LEVEL_ID'))
			if procLev == 3:
				scetDim=2
				temp=[out[i] for i  in range(self._dim[0], len(out), self._dim[0]+1)]
				temp=filter(lambda a: a !=0,temp)
				tmp2=struct.pack(len(temp)*'L',*temp)
				tmp2=struct.unpack((len(temp))*'HH',tmp2)
				scet=array(tmp2[::2]).reshape((self._dim[2],3),order='C')
				rawData=array(out).reshape(shape,order='F')
				data=rawData[0:self._dim[0],:,:]
				fl.seek((dataPos*recByte)+coreBlock)
				buff=fl.read()
				bott=struct.unpack_from(('>'+(3*self._dim[0]*self._dim[1])*'f'),buff)
				bott=array(bott).reshape((self._dim[0],self._dim[1],3),order='F')
				self._qube=data
				self._scet=scet
				self._table=bott
			elif procLev == 2:
				data=array(out).reshape(shape,order='F')
				self._qube=data[:,0:-1,:]
				tmp=list(data[:,-1,:].reshape((self._dim[0]*self._dim[2]),order='F'))
				tmp2=struct.pack(len(tmp)*'h',*tmp)
				hk=struct.unpack_from(len(tmp)*'H',tmp2)
				tmp=array(hk).reshape((self._dim[0],self._dim[2]),order='F')
				tmp2=tmp[0:(82*5),:]
				self._HK=tmp2.reshape((82,5,self._dim[2]),order='F')
				self._HKName=['Data SCET-1','Data SCET-2','Data SCET-3','Acquisition ID','# of subslices + 1st serial #','Data Type','SPARE','ME_default HK SCET-1','ME_default HK SCET-2','ME_default HK SCET-3','V_MODE','ME_PWR_STAT','ME_PS_TEMP','ME_DPU_TEMP','ME_DHSU_VOLT','ME_DHSU_CURR', 'EEPROM_VOLT','IF_ELECTR_VOLT','SPARE','M_ME_general HK SCET-1','M_ME_general HK SCET-2','M_ME_general HK SCET-3','M_ECA_STAT','M_COOL_STAT', 'M_COOL_TIP_TEMP','M_COOL_MOT_VOLT','M_COOL_MOT_CURR','M_CCE_SEC_VOLT','SPARE','MVIS_HK_report SCET-1','MVIS_HK_report SCET-2','MVIS_HK_report SCET-3','M_CCD_VDR_HK','M_CCD_VDD_HK','M_+5_VOLT','M_+12_VOLT','M_-12_VOLT','M_+20_VOLT','M_+21_VOLT','M_CCD_LAMP_VOLT','M_CCD_TEMP_OFFSET','M_CCD_TEMP','M_CCD_TEMP_RES','M_RADIATOR_TEMP','M_LEDGE_TEMP','OM_BASE_TEMP','H_COOLER_TEMP','M_COOLER_TEMP','M_CCD_WIN_X1','M_CCD_WIN_Y1', 'M_CCD_WIN_X2','M_CCD_WIN_Y2','M_CCD_DELAY','M_CCD_EXPO','M_MIRROR_SIN_HK','M_MIRROR_COS_HK','M_VIS_FLAG_ST','SPARE','MIR_HK_report SCET-1', 'MIR_HK_report SCET-2','MIR_HK_report SCET-3','M_IR_VDETCOM_HK','M_IR_VDETADJ_HK','M_IR_VPOS','M_IR_VDP','M_IR_TEMP_OFFSET','M_IR_TEMP', 'M_IR_TEMP_RES','M_SHUTTER_TEMP','M_GRATING_TEMP','M_SPECT_TEMP','M_TELE_TEMP','M_SU_MOTOR_TEMP','M_IR_LAMP_VOLT','M_SU_MOTOR_CURR', 'M_IR_WIN_Y1','M_IR_WIN_Y2','M_IR_DELAY','M_IR_EXPO','M_IR_LAMP_SHUTTER','M_IR_FLAG_ST','SPARE']
			else:
				print 'No case'
				print procLev
				sys.exit()
		elif self._dataType =='VIRTIS GEOMETRY':
			rawData=array(out).reshape(shape,order='F')
			geoCoeff=[0.0001]*33
			geoCoeff=array(geoCoeff)
			geoCoeff[13:14]=0.001
			geoCoeff[15]=0.00001
			geoCoeff[29]=0.001
			geoCoeff[32]=1
			geoNam=['Surf longit, corner1','Surf longit, corner2','Surf longit, corner3','Surf longit, corner4','Surf latit, corner1','Surf latit, corner2','Surf latit, corner3','Surf latit, corner4','Surf longit, center','Surf latit, center','Incidence at surf','Emergence at surf','Phase at surf','Elevation on surf layer','Slant distance','Local time','Cloud longit, corner1','Cloud longit, corner2','Cloud longit, corner3','Cloud longit, corner4','Cloud latit, corner1','Cloud latit, corner2','Cloud latit, corner3','Cloud latit, corner4','Cloud longit, center','Cloud latit, center','Incidence on clouds','Emergence on clouds','Phase on clouds','Elevation below clouds','Right ascension','Declination','M-common frame']
			self._geoName=geoNam
			self._geoCoeff=geoCoeff
			data=rawData
			self._qube=data
		fl.close()
		
