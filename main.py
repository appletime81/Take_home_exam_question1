import re
import pandas as pd
import xml.etree.ElementTree as ET

from glob import glob


def get_files():
    return glob('*.xml')


def convert_xml_to_df(fileName):
    tree = ET.parse(fileName)
    root = tree.getroot()

    # get column names
    col_names = []
    for child in root[0]:
        col_names.append(child.tag)

    # init dictionary
    data_dict = {}
    for col_name in col_names:
        data_dict[col_name] = list()

    # insert data to dictionary
    for child in root:
        for sub_child in child:
            data_dict[sub_child.tag].append(sub_child.text)

    # convert dictionary to dataframe
    df = pd.DataFrame(data_dict)
    return df


def main():
    xml_files = get_files()
    df_list = []
    for xml_file in xml_files:
        df_list.append(convert_xml_to_df(fileName=xml_file))

    df_all = pd.concat(df_list, ignore_index=True)
    df_all["建物現況格局-廳"] = pd.to_numeric(df_all["建物現況格局-廳"])

    # q1.
    level = list(df_all['總樓層數'].unique())
    level_limit = ['一層', '二層', '三層', '四層', '五層', '六層', '七層', '八層', '九層', '十層',
                   '十一層', '十二層', '十三層']
    level_condition = [x for x in level if x not in level_limit]
    level_condition.remove(None)

    filter_a = df_all[(df_all['總樓層數'].isin(level)) &
                      (df_all['主要用途'] == '住家用') &
                      (df_all['建物型態'].str.contains('住宅大樓'))]
    # print(filter_a)
    filter_a.to_csv('filter_a.csv', index=False, encoding='utf-8-sig')

    # q2.
    # 計算總件數(calculate total object numbers)
    total_objet_number = df_all.shape[0]

    # 計算算總車位數
    total_parking_place = 0
    for i in range(len(df_all['交易筆棟數'])):
        res = re.findall(r'\d+', df_all['交易筆棟數'][i])
        index = len(res) - 1
        total_parking_place += int(res[index])

    # 計算平均總價元
    df_all['總價元'] = pd.to_numeric(df_all['總價元'])
    total_price = df_all['總價元'].sum(axis=0, skipna=True)
    mean_price = total_price / total_objet_number

    # 計算平均車位總價元
    df_all['車位總價元'] = pd.to_numeric(df_all['車位總價元'])
    total_parking_place_price = df_all['車位總價元'].sum(axis=0, skipna=True)
    mean_parking_place_price = total_parking_place_price / total_objet_number

    dict_ = {
        '總件數': [total_objet_number],
        '總車位數': [total_parking_place],
        '平均總價元': [mean_price],
        '平均車位總價元': [mean_parking_place_price]
    }
    filter_b = pd.DataFrame(dict_)
    filter_b.to_csv('filter_b.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()
