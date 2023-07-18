import pandas as pd
import streamlit as st
import re

def process_column(df, column_idx):
    result = []
    for value in df.iloc[:, column_idx]:
        result.append(value)
    return result


def extract_metric(text, measures):
    result = {}
    for measure in measures:
        result[measure] = None
    
    for measure in measures:
        if text is not None:
            attri = measure
            text_for_position = text
            pos = 0
            while pos == 0:
                pos = re.search(attri, text_for_position)
                if pos is None:
                    break
                if re.search(r"[0-9]", text_for_position[pos.end()]):
                    pos = pos.start()
                else:
                    text_for_position = text_for_position[pos.start()+1:]
                    pos = 0
            if pos is not None and pos > 0:
                text_sub = text_for_position[pos + len(attri):]
                pos_stop = re.search(r"[^0-9.-]", text_sub)
                if pos_stop is not None:
                    value = text_sub[:pos_stop.start()]
                    pos_unit = re.search(r"厘米|毫米", text_sub)
                    if pos_unit is not None:
                        unit = text_sub[pos_unit.start():pos_unit.end()+1]
                        value_unit = value + unit
                        result[measure] = value_unit[:-1]  # 去掉最后一个字符
    
    result = {k: "NAN" if v is None else str(v) for k, v in result.items()}
    return result


def extract_nonmetric(text, measurements):
    result = {}
    for measurement in measurements:
        result[measurement] = 0  # 默认值为0

    if text is not None:
        for measurement in measurements:
            if re.search(measurement, text):
                result[measurement] = 1  # 匹配到了，将值设为1

    return result



def generate_dataframe(names, texts, process_function,fun_value):
    data = {}
    # 遍历每个name和text对应的值
    for name, text in zip(names, texts):
        # 使用处理函数处理文本，生成字典
        processed_dict = process_function(text,fun_value)
        # 将字典的键值对添加到data字典中
        for key, value in processed_dict.items():
            if key not in data:
                data[key] = []
            data[key].append(value)
    # 创建数据框
    df = pd.DataFrame(data)
    # 添加name列
    df.insert(0, "name", names)
    return df



st.title("考古报告描述信息量化")

file = st.file_uploader("导入csv格式文件(excel格式可另存为):")
name_col = st.number_input("名称(编号)列号",value=1)
description_col = st.number_input("描述列的列号",value=2)

metric_df = pd.DataFrame(
    {
        "测量值": ['长','残长','高','残高', '通高','宽','残宽','粗','厚','孔径','口径'],
        "选项": [False] * 11,
    }
)

nonmetric_df = pd.DataFrame(
    {
        "离散值": ['泥质', '夹砂', '石灰岩', '矽质灰岩', '变晶辉长岩', '辉绿岩', '变晶长英岩', 
        '假鲕状灰岩', '片麻岩', '钙质硬岩', '粘板岩', '大理岩', '辉长岩', '闪长岩', '霏细岩', 
        '页岩', '砂岩', '骨', '猪獠牙', '蚌壳', '矽质鲕状灰岩', '鲕状灰岩', '花岗岩', '兽胫骨',
        '兽肢骨', '牙质', '角闪片麻岩', '兽骨', '石质', '陶质', '磨制', '管穿', '琢穿', '旋穿',
        '两面对磨', '褐', '青', '黑', '红', '灰', '白', '绿', '淡白', '淡青', '乳白', '淡黄色', 
        '深灰色', '黄', '紫', '灰白', '淡绿', '灰褐', '黑彩', '红彩', '朱彩', '白彩', '朱色', 
        '红色', '宽沿', '窄沿', '尖唇', '尖圆唇', '圆唇', '大口', '小口', '厚唇', '薄唇', '方唇', 
        '敞口', '敛口', '直口', '侈口', '口沿平折', '折沿', '宽弧沿', '内敛', '口微敛', '沿向外斜卷',
        '深横槽', '斜腹', '深腹', '垂腹', '直腹', '圆腹', '折腹', '深圆腹', '扁圆腹', '椭圆腹', 
        '缓折腹', '宽腹', '浅腹', '长颈', '高颈', '粗颈', '短颈', '平肩', '宽肩', '圆肩', '近直',
        '平底', '磨平', '竖鼻', '横鼻', '矮凿形足', '矮三角形扁足', '矮三角形凿足', 
        '喇叭形高圈足', '高凿形足', '三角形凿足', '扁三角形足', '扁弯凿足', '短三角形凿足', 
        '矮板凿形足', '三角形扁足', '素面', '光泽', '明亮', '戳印纹', '辐射条纹', '带纹', 
        '三角形纹', '水波纹', '弦纹', '连三角形', '连弧纹', '连三角网纹', '三角形内网纹', '连三角纹',
        '平行线', '复道', '菱形', '涡纹', '下弦纹', '白点带纹', '圆点纹', '菱形网纹', '同心圆',
        '宽带纹', '平行竖道', '网纹', '锯齿纹', '宽带网纹', '曲线纹', '压点纹', '锯齿形凸弦纹',
        '附加堆纹', '篮纹', '圆锥体', '圆柱体', '舌状', '长方形', '扁平梯形', '扁平长方形', 
        '扁薄长方形', '扁平长条形', '短梯形', '斜三角形', '长条形', '近矩形', '月牙形', '扁圆形',
        '三角形', '楔形', '扁平长梯形', '半月形', '不规则圆柱状', '凸字形', '方锤形', '类无柄短剑',
        '柳叶形', '圆柱形', '圆锥形', '圆筒形', '壶形', '碗形', '钵形', '覆碗形', '弧刃', '斜弧刃',
        '未开刃', '三面刃', '斜齐刃', '单面齐刃', '齐刃', '齐刃较钝', '两面刃', '单刃', '圆孔', 
        '大孔', '小孔', '无穿孔', '半月形', '长方孔', '圆角长方形', '近方形', '方形', '长方形', 
        '半月形', '平顶', '方平顶', '横槽', '竖槽', '穿孔', '平顶', '圆帽形', '弧曲', '斜直', 
        '有段', '有穿孔', '三棱形', '细长', '锐利', '倒钩', '锥形', '短铤', '扁片形', '薄片形', '锥形', '扁薄'],
        "选项": [False] * 219,
    }
)

st.sidebar.title("勾选需要导出的变量:")

edited_metric_df=st.sidebar.data_editor(
    metric_df,
    column_config={
        "选项": st.column_config.CheckboxColumn(
            "选择需要的连续变量",
            help="选择需要的连续变量",
            default=False,
        )
    },
    disabled=["测量值"],
    hide_index=True,
)

edited_nonmetric_df=st.sidebar.data_editor(
    nonmetric_df,
    column_config={
        "选项": st.column_config.CheckboxColumn(
            "选择需要的离散变量",
            help="选择需要的离散变量",
            default=False,
        )
    },
    disabled=["离散值"],
    hide_index=True,
)
# 提取选择的部分

nonmetric_values = edited_nonmetric_df[edited_nonmetric_df["选项"]]["离散值"].tolist()
metric_values = edited_metric_df[edited_metric_df["选项"]]["测量值"].tolist()

# 显示选择结果
cola, colb = st.columns(2)
# 在第一列显示第一个表格
with cola:
    st.write("您选择的连续变量：", metric_values)

# 在第二列显示第二个表格
with colb:
    st.write("您选择的离散变量：", nonmetric_values)




##############################################执行操作#
data=pd.read_csv(file,encoding="gbk")
name_lists = process_column(data,name_col)
result_lists = process_column(data,description_col)
result_lists = ['无' if pd.isna(x) else x for x in result_lists]

metric_result=generate_dataframe(name_lists,result_lists,extract_metric,metric_values)
nonmetric_result=generate_dataframe(name_lists,result_lists,extract_nonmetric,nonmetric_values)
# 使用 st.beta_columns() 创建两列
col1, col2 = st.columns(2)

# 在第一列显示第一个表格
with col1:
    st.subheader("连续变量表格")
    st.table(metric_result)
    st.download_button(
          label='Download metric_result.csv',
          data=metric_result.to_csv(index=False),
          file_name='metric_result.csv',
          mime='text/csv'
      )

# 在第二列显示第二个表格
with col2:
    st.subheader("离散变量表格")
    st.table(nonmetric_result)
    st.download_button(
          label='Download nonmetric_result.csv',
          data=nonmetric_result.to_csv(index=False),
          file_name='nonmetric_result.csv',
          mime='text/csv'
      )
    

