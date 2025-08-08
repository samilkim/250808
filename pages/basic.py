import streamlit as st

st.title("팔팔샘 스트림릿 연습장")
st.write("스트림릿을 배우기 위해 이것저것 시도해보고 있습니다.")
st.write("오늘은 2일차 입니다!!")
st.success("오늘은 스트림릿으로 다양한 데이터 프로젝트를 진행합니다.")

st.divider()
st.title("2행 2열 예제 ")

내용 = ""

col1, col2 = st.columns(2)
if col1.button("사랑"): 내용 = "사랑합니다."
if col2.button("겸손"): 내용 = "존경합니다."

col3, col4 = st.columns(2)
if col3.button("실존"): 내용 = "제가 할게요."
if col4.button("협력"): 내용 = "함께합시다."

st.markdown(f"# {내용}")

열1, 열2, 열3= st.columns(3)
with 열1:
    st.image("https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzA2MDFfMTc5%2FMDAxNjg1NTgxMjc5NTU5.4FQqSUSZeUxGqtl58Bm5WhCOBgC1MXR9Wi612o3blusg.XpwNRSwpktqSPxGUBI0q_lRqTm_vxw4tVAH1nZWEIgwg.JPEG.eunbyeol5044%2FIMG_6089.jpg&type=sc960_832", width =300)
    st.caption("삼일고 사진")
with 열2:
    st.image("https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzA5MjFfMTEz%2FMDAxNjk1Mjg4NTU2MzIw.OpUi3mRaSKLjlHPk24qnLFOpqvQDSglam8mgDSa7TFYg.VM03MZnzqUoLdGP0xHi5GIEVF0_Yda47llRp1GBBXywg.PNG.jshtej8075%2F4.PNG&type=sc960_832", width = 300)
    st.caption("삼일고 마크")
with 열3:
    st.image("son.jpg")

