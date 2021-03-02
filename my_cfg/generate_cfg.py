import sys
from datetime import datetime
import os
from os.path import join as jpath

sys.path.append('../')

class GenerateConfig:
    def __init__(self, config):
        self.config = config
        self.cfg_file_lines = 'Error'

    def _get_conf(self):
        if self.config['type'] == 'yolov4':
            with open('my_cfg/yolov4.cfg', 'r+') as f:
                self.cfg_file_lines = f.readlines()
        
        elif self.config['type'] == 'yolov4-tiny':
            with open('my_cfg/yolov4-tiny.cfg', 'r+') as f:
                self.cfg_file_lines = f.read()
        
        elif self.config['type'] == 'yolov4-tiny-3l':
            with open('my_cfg/yolov4-tiny-3l.cfg', 'r+') as f:
                self.cfg_file_lines = f.readlines()
        
        elif self.config['type'] == 'yolov4-csp':
            with open('my_cfg/yolov4-csp.cfg', 'r+') as f:
                self.cfg_file_lines = f.readlines()
        else:
            self.cfg_file_lines = 'Error'
            error_msg = '[ERROR] There is no yolo type like that. Check again!'
            print(error_msg)

    def _get_basename(self):
        now = datetime.now() # current date and time
        time_now = now.strftime("%m%d%Y_%H%M%S")
        version = [time_now if str(self.config['version-config']) == 'auto' else str(self.config['version-config'])][0]

        base_name = str(self.config['type'])
        base_name += '_'
        base_name += str(self.config['name-project']) 
        base_name += '_'
        base_name += version
        return base_name

    def generate_makefile(self):
        with open('Makefile', 'r+') as f:
            makefiles = f.read()
            for param in self.config.keys():
                if param+'_mine' in makefiles:
                    makefiles = makefiles.replace(param+'_mine', str(self.config[param]))
        
        with open('Makefile', 'w') as f:
            f.write(makefiles)
        print('[DONE] generate Makefile')

    def generate_path_setting(self, path_dataset):
        basename = self._get_basename()

        def remove_none(x):
            if x == '\n':
                return False
            return True

        with open(f'{path_dataset}/label.names', 'r') as f:
            hai = f.readlines()
            hai = list(filter(remove_none, hai))
            self.num_class = len(hai)

        # update configs
        self.config['classes'] = self.num_class
        self.config['filters_conv'] = (self.num_class+5) * 3
        self.config['max_batches'] = (self.num_class) * 2000
        self.config['step_1'] = int(0.8 * self.config['max_batches'])
        self.config['step_2'] = int(0.9 * self.config['max_batches'])


        root = f'{basename}/data_desc'
        self.obj_data_path = jpath(basename, 'data_desc')
        if not os.path.exists(root): os.makedirs(root)
        with open(f'{root}/obj.data', 'w') as f:
            f.write(f'classes = {self.num_class}\n')
            f.write(f'train   = {root}/train.txt\n')
            f.write(f'valid   = {root}/valid.txt\n')
            f.write(f'names   = {root}/obj.names\n')
            f.write(f'backup  = {root}/backup/')

        train_txt = f'{root}/train.txt'
        valid_txt = f'{root}/valid.txt'

        
        with open(train_txt, 'w') as f:
            for img in [f for f in os.listdir(jpath(path_dataset, 'train')) if f.endswith('jpg')]:
                path_full_img = jpath(path_dataset, 'train', img)
                f.write(path_full_img+'\n')

        with open(valid_txt, 'w') as f:
            for img in [f for f in os.listdir(jpath(path_dataset, 'valid')) if f.endswith('jpg')]:
                path_full_img = jpath(path_dataset, 'valid', img)
                f.write(path_full_img)

        os.makedirs(jpath(root), 'backup')
        os.makedirs(jpath(basename), 'inference')

        print('here your configs path:')
        print(f'''
        └── {basename}
           ├── {basename}.cfg
           ├── {data_desc}
           │    ├── train.txt 
           |    ├── valid.txt 
           |    ├── obj.names
           |    └── backup/
           └── inference/
        ''')
        
    def generate_arch_config(self):
        self._get_conf()

        if self.cfg_file_lines == 'Error':
            print('[ERROR] Failed to generate configs')
            return
        basename = self._get_basename()
        name_cfg = basename +'.cfg'
        cfg_file = jpath(basename, name_cfg)
        self.cfg_path = cfg_file
        if not os.path.exists(basename):
            os.makedirs(basename)
        
        with open(cfg_file, 'w') as f:
            for params in self.config.keys():
                if params+'_mine' in self.cfg_file_lines:
                    self.cfg_file_lines = self.cfg_file_lines.replace(params+'_mine', str(self.config[params]))
                    print(params+'_mine', str(self.config[params]))
            f.write(self.cfg_file_lines)
        
        print('[DONE] see result on', f'"{cfg_file}"')

    def update_config(self, config):
        self.config.update(config)

    def generate_command(self, mode):
        self.downloaded_path = 'yolov4.conv.137'
        print('COPY THIS to new cell, and Excecute!\n\n')
        if mode=='train':
            print(f''' 
            " 
            !darknet detector train \ \n{self.obj_data_path} \ \n{self.cfg_path} \n{self.downloaded_path} -dont_show -map
            "''')

    def get_basename(self):
        return self._get_basename()

if __name__ == '__main__':
    config = {}
    makefile_config = { 
        # Makefile
        'gpu' : 0,
        'cudnn': 0,
        'cudnn_half':0,
        'opencv':0,
        'avx':0,
        'openmp':0,
        'libso': 0,
        'zed_cam': 0,
        'zed_cam2': 0,
        'compute_compability': 75,
    }

    arch_config = {
        # architecture yolo-configs
        'name-project': 'badak', # no space
        'version-config': 'auto', # or 'auto' will generate date
        'type' : 'yolov4-tiny', # (tiny, tiny-3l, csp, normal)
        'batch': 164,
        'subdivisions': 8,
        'width': 512,
        'height': 256
    }

    config.update(makefile_config)
    config.update(arch_config)

    cfg = GenerateConfig(config)
    # cfg.generate_makefile()

    cfg.generate_path_setting('YOUR_CUSTOM_DATA')
    cfg.generate_config()

    cfg.generate_command(mode='train')

    # cek nvidia-env, get compute comp
    # conf makefile
    # update_config()
    # generate makefile
    # !make

    # download weights base type-yolo

    # download dataset
    # setting obj.data
    # generate config

    # train


