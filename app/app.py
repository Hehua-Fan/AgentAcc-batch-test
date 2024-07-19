import streamlit as st
import pandas as pd
import openai
from agent_eval import agent_eval
import plotly.graph_objects as go
from configs import ZHIPU_AI_API_KEY, OPEN_AI_API_KEY, OPEN_AI_BASE_URL, AUTOAGENTS_HOST_NAME
from qa_pair_generator import qa_pair_generator
from page_config import page_config
from agent_info import agent_info
from utils import load_data, get_default_data, download_file, create_aggrid, get_default_data_without_expectation


def main():
    # 环境变量
    host = AUTOAGENTS_HOST_NAME
    openai.api_key = OPEN_AI_API_KEY
    openai.base_url = OPEN_AI_BASE_URL

    # 网页设置
    page_config()

    # 主页面标题
    st.title("Agent准确率批量测试 🚀")

    # Sidebar
    with st.sidebar:
        # 板块 1: 问答对生成器（选用工具）
        qa_pair_generator()
        
        # 板块 2: 下载测试模板
        with st.expander("📥 下载测试模板"):
            st.write("可在本地编辑测试模版")
            template_df = get_default_data()
            download_file(label='下载测试结果文件.xlsx',file_name='测试模板.xlsx', df=template_df)

        # 板块 3: Agent信息填写
        uuid, authkey, authsecret = agent_info()
            
        file_uploaded = st.file_uploader("**上传你的测试模版(.csv或.xlsx)**")

        IsEvaluate = st.checkbox("开启Agent准确率计算", value=True)

    # 数据加载和显示
    if not IsEvaluate:
        if file_uploaded is None:
            df = get_default_data_without_expectation()
        else:
            df = load_data(file_uploaded)
            df['Agent回答'] = ''
    else:
        if file_uploaded is None:
            df = get_default_data()
        else:
            df = load_data(file_uploaded)
            if df is not None and 'Agent回答' not in df.columns:
                df['Agent回答'] = ''
            if df is not None and '是否正确' not in df.columns:
                df['是否正确'] = ''

    # Dashboard
    st.subheader("📊 测试数据")
    start_test = st.button('🚀 开始批量测试！', key='start_test_button', disabled=not all([uuid, authkey, authsecret]))

    grid_response = create_aggrid(df)
    df = grid_response

    if not all([uuid, authkey, authsecret]):
        st.warning('⚠️ 请在侧边栏填写🤖Agent信息')
    elif start_test:
        with st.spinner('正在进行测试...'):
            result_df, acc = agent_eval(df, host, uuid, authkey, authsecret, IsEvaluate)
        
        # 更新原有表格的数据
        df['Agent回答'] = result_df['Agent实际输出']
        if IsEvaluate:
            df['是否正确'] = result_df['是否准确']

        st.write("") 
        st.subheader("🔍 测试结果")
        if IsEvaluate:
            st.metric("Agent回答准确率：", f"{acc:.2%}")
        create_aggrid(df, editable=False)

        # 下载测试结果文件
        download_file(label='下载测试结果.xlsx',file_name='测试结果.xlsx', df=df)


if __name__ == '__main__':
    main()

    # streamlit run app/app.py