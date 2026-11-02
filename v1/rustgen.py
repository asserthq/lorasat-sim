import os

import db
from pysimscheduler import libKernel


def gen_rust(m, rsfile):
    fType = 'f32' if libKernel.FLOAT_TYPE == 'f' else 'f64'
    code = '// Файл создаётся автоматически, не редактируйте его!\n\n'
    code += '#[repr(C)]\n'
    code += '#[allow(non_snake_case)]\n'
    code += 'pub struct Db {\n'
    for key in m.Keys:
        n = len(m.Types[key]['str'])
        typ = m.Types[key]['type']
        if typ == 'f':
            code += f'    pub {key}: {fType},\n'
        elif typ == 'a' or typ == 'q':
            code += f'    pub {key}: [{fType}; {n}],\n'
        elif typ == 'i':
            code += f'    pub {key}: i32,\n'
    code += '}\n\n'
    addr, port = m.TaskList[m.task.name]['Addr']
    code += 'pub const DB_SIZE: usize = std::mem::size_of::<Db>();\n'
    code += f'pub const COM_ADDRESS: &str = "{addr}";\n'
    code += f'pub const COM_PORT: u16 = {port};\n'
    with open(rsfile, 'w', encoding='utf-8') as f:
        f.write(code)
    print(code)


class Rust(libKernel.TaskTemplate):
    pass


os.makedirs(f"{db.OUTPUT_DIR}/gen", exist_ok=True)
model = Rust(TaskList=db.Tasks, DB=db.DataBase())
gen_rust(model.Manager, f"{db.OUTPUT_DIR}/gen/db.rs")