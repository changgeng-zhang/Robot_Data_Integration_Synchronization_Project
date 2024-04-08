from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ReportingPerson:
    reportingName: str
    position: str
    erpUserCode: str


@dataclass
class Class:
    className: str
    deviceGoodQuantity: int
    deviceWasteQuantity: int
    deviceWasteReason: str
    deviceReportingNames: str
    reportingPersonList: List[ReportingPerson]
    reportingTime: datetime
    startProductionDate: datetime
    reportingId: int
    startReportTime: datetime
    rpaScheduleNo: str
    rpaMachineTool: str
    erpProcessType: str
    erpScheduleObjId: str
    erpMachineRemark: str
    processSource: int


@dataclass
class Device:
    deviceName: str
    classes: List[Class]


@dataclass
class Process:
    index: int
    processName: str
    processEndTime: str
    goodQuantity: int
    wasteQuantity: int
    devices: List[Device]


@dataclass
class ProductionOrder:
    boxOrderCode: str
    orderStatus: int
    productNo: str
    productName: str
    processes: List[Process]


@dataclass
class ResultData:
    resultCode: int
    resultMsg: str
    resultData: List[ProductionOrder]
