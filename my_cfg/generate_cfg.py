import sys
from datetime import datetime
import os
from os.path import join as jpath

sys.path.append('../')

class GenerateConfig:
    def __init__(self, config):
        self.config = config
        self.cfg_file_lines = 'Error'
        self.config['name-project'] = self.config['name-project'].upper()
        self.config['version-config'] = self.config['version-config'].upper()

    def _get_conf(self):
        if self.config['arch'] == 'yolov4':
            with open('my_cfg/yolov4.cfg', 'r+') as f:
                self.cfg_file_lines = f.read()
        
        elif self.config['arch'] == 'yolov4-tiny':
            with open('my_cfg/yolov4-tiny.cfg', 'r+') as f:
                self.cfg_file_lines = f.read()
        
        elif self.config['arch'] == 'yolov4-tiny-3l':
            with open('my_cfg/yolov4-tiny-3l.cfg', 'r+') as f:
                self.cfg_file_lines = f.read()
        
        elif self.config['arch'] == 'yolov4-csp':
            with open('my_cfg/yolov4-csp.cfg', 'r+') as f:
                self.cfg_file_lines = f.read()
        else:
            self.cfg_file_lines = 'Error'
            error_msg = '[ERROR] Ups! we didnt have arch like that. Check again!'
            error_msg += '\nArchitecture:\n- yolov4\n- yolov4-tiny\n- yolov4-csp\n- yolov4-tiny-3l'
            print(error_msg)

    def _get_parent_folder(self):
        '''
        cuman name-project+version
        '''
        now = datetime.now() # current date and time
        time_now = now.strftime("%m%d%Y_%H%M%S")
        version = [time_now if str(self.config['version-config']) == 'auto' else str(self.config['version-config'])][0]
        
        base_name = str(self.config['name-project']) 
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
        self.config['steps_1'] = int(0.8 * self.config['max_batches'])
        self.config['steps_2'] = int(0.9 * self.config['max_batches'])

        # config name
        parent_folder = self._get_parent_folder()
        root = f'{parent_folder}/data_desc'
        self.full_model_name = f'{self.config["arch"]}_{self.config["subversion"]}'
        self.full_name = f'{self.full_model_name}_{parent_folder}'
        self.name_cfg = self.full_name + '.cfg'
        self.obj_data_path = jpath(parent_folder, 'data_desc','obj.data')
        self.backup_path = jpath(root, f'backup_{self.full_model_name}')
        self.infer_path = jpath(parent_folder, f'inference_{self.full_model_name}')


        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
        
        if not os.path.exists(self.infer_path):
            os.makedirs(self.infer_path)


        if not os.path.exists(root): os.makedirs(root)
        with open(f'{root}/obj.data', 'w') as f:
            f.write(f'classes = {self.num_class}\n')
            f.write(f'train   = {root}/train.txt\n')
            f.write(f'valid   = {root}/valid.txt\n')
            f.write(f'names   = {root}/obj.names\n')
            f.write(f'backup  = {root}/{self.backup_path}/')

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


        print('here your configs path:')
        print(f'''
        └── {parent_folder}
           ├── {self.name_cfg}
           ├── data_desc
           │    ├── train.txt 
           |    ├── valid.txt 
           |    ├── obj.names
           |    └── backup_{self.full_model_name}/
           └── inference_{self.full_model_name}/
        ''')
        
    def generate_arch_config(self):
        self._get_conf()

        if self.cfg_file_lines == 'Error':
            print('[ERROR] Failed to generate configs')
            return
        parent_folder = self._get_parent_folder()
        cfg_file = jpath(parent_folder, self.name_cfg)
        self.cfg_path = cfg_file
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)
        
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
            **************************************************
            !darknet detector train \ 
                {self.obj_data_path} \ 
                {self.cfg_path} \ 
                {self.downloaded_path} -dont_show -map \
                2>&1 | tee {self.backup_path}/train.log | grep -E "hours left|mean_average"
            **************************************************''')
        return self.obj_data_path, self.cfg_path, self.downloaded_path
    
    def get_parent_folder(self):
        return self._get_parent_folder()

    def get_fullname(self):
        '''
            self.full_model_name = f'{self.config["arch"]}_{self.config["subversion"]}'
            self.full_name = f'{self.full_model_name}_{parent_folder}'
        '''
        return self.full_name

    def get_model_backup_path(self):
        return self.backup_path


    def get_pretrained_models(self):
        yolov4 = 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights'
        yolov4_csp = 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-csp.weights'
        yolov4_tiny = 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights'
        
        if self.config['arch'] == 'yolov4':
            link = yolov4
            name_pretrained = 'yolov4.weights'
        elif self.config['arch'] == 'yolov4-tiny':
            link = yolov4_tiny
            name_pretrained = 'yolov4-tiny.weights'
        elif self.config['arch'] == 'yolov4-csp':
            link = yolov4_csp
            name_pretrained = 'yolov4-csp.weights'
        else:
            link = ''
            name_pretrained = ''
        
        self.downloaded_path = name_pretrained
        return link, name_pretrained
        
    def show_chart_training(self):
        print('Cooming soon!')
        pass

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


