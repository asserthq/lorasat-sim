import db
from pysimscheduler import libKernel


class ADCS(libKernel.TaskTemplate):
    pass


model = ADCS(TaskList=db.Tasks, DB=db.DataBase())
model.Manager.genCHeader(f"{db.OUTPUT_DIR}/gen/db.h")
