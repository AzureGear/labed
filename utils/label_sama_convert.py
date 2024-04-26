import json
import sys
import re


# "path_to_images": "F:\\data_sets\\test_oil_ref\\"

# Структура файла SAMA (Романа Хабарова)
# data["path_to_images"] = "one_path"
#  └- data["images"] = {"one.jpg", "two.jpg", ... "n.jpg"}
#      └- data["labels"] = []
#          └- data["labels_color"] = {}



{
	"path_to_images":"F:\\data_sets\\test_oil_ref\\",
	"images":
		{"154s_HUN_2019-08.jpg":
			{"shapes":
				[{"cls_num":0,
				  "id":0,
				  "points":
					[[708.9772254617831,803.994791760785],[725.0571212969988,829.3328094405188],[653.4284943946743,875.6234186631094],[636.3740594179304,851.2599401249038]]
				}],
				"lrm":0.20257005180040008,
				"status":"empty",
				"last_user":null
			}
		},"labels":["building"],"labels_color":{"building":[170,0,0,120]}

}


def convert_labelme_to_sama(input_files, output_file):
    data = ["test", "test", "test"]
    with open(output_file, 'w+') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def load(self, json_path):  # Роман Хабаров реализация
    with open(json_path, 'r', encoding='utf8') as f:
        self.data = ujson.load(f)
        self.check_and_convert_old_data_to_new()
        self.update_ids()
        self.is_loaded = True