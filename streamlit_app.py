#!/usr/bin/env python3
"""课后反馈生成器 - Streamlit Web版
部署在 Streamlit Cloud 上，使用 Turso 云数据库
"""

import os
import requests
import streamlit as st
from datetime import datetime

# 尝试导入AI反馈模块
try:
    from ai_feedback import AIFeedbackGenerator
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False

    class AIFeedbackGenerator:
        def generate_coach_feedback(self, *args, **kwargs):
            return "AI反馈模块不可用，请检查依赖安装"

# 尝试导入Turso数据库
try:
    from turso_db import TursoDB
    TURSO_AVAILABLE = True
except Exception:
    TURSO_AVAILABLE = False

# ===== 配置 =====
SYSTEMS_CONFIG = {
    "yingxiaowu": {
        "base_url": os.getenv("YXW_BASE_URL", "https://yxw6-api.yingxiaowu.cn"),
        "teacher_id": int(os.getenv("YXW_TEACHER_ID", "675424")),
        "default_token": os.getenv(
            "YINGXIAOWU_TOKEN",
            "eyJhbGciOiJIUzUxMiJ9.eyJjcmVhdGVkIjoxNzgyNTM3MTYyNjQ5LCJzdWIiOiI2NzU0MjQiLCJleHAiOjE4MTM2NDExNzJ9.jYlkdg9z22G_jUx06uIMl8xR7OV_divzmU1ljeu6BoekaKMiayvxNE_AVxdw9yD1wxgRCXMeNkjCO6td0hV72A",
        ),
    },
    "entopia": {
        "base_url": os.getenv("ENT_BASE_URL", "https://api6.entopia.cn"),
        "teacher_id": int(os.getenv("ENT_TEACHER_ID", "539191")),
        "default_token": os.getenv(
            "ENTOPIA_TOKEN",
            "eyJhbGciOiJIUzUxMiJ9.eyJjcmVhdGVkIjoxNzgyOTg4MTkyNTk3LCJzdWIiOiI1MzkxOTEiLCJleHAiOjE4MTQwOTIyMDJ9.AWpEkaVT6y3NUQ2KnWzm-0CuncWimus9n-iJelLkYkZG-VzsTH15twnz3rZvI7sSRx97VND9yUxVXnKVB_57mg",
        ),
    },
}

STUDENTS_CONFIG = {
    "原诗雯": {"student_id": "709807", "system": "yingxiaowu"},
    "张嘉怡": {"student_id": "1393883", "system": "yingxiaowu"},
    "关云丹": {"student_id": "1394684", "system": "yingxiaowu"},
    "吴靖宇": {"student_id": "695523", "system": "entopia"},
}


# ===== 初始化状态 =====
def init_state():
    if "course_data" not in st.session_state:
        st.session_state.course_data = []
    if "course_data_child" not in st.session_state:
        st.session_state.course_data_child = ""
    if "forget_course_data" not in st.session_state:
        st.session_state.forget_course_data = []
    if "forget_course_data_child" not in st.session_state:
        st.session_state.forget_course_data_child = ""
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "token_store" not in st.session_state:
        st.session_state.token_store = {
            "yingxiaowu": SYSTEMS_CONFIG["yingxiaowu"]["default_token"],
            "entopia": SYSTEMS_CONFIG["entopia"]["default_token"],
        }
        # 从Turso加载Token
        if TURSO_AVAILABLE:
            db = TursoDB()
            for system in ["yingxiaowu", "entopia"]:
                token = db.get_token(system)
                if token:
                    st.session_state.token_store[system] = token


def add_log(message):
    time_str = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{time_str}] {message}")


def get_system_config(system_name):
    config = SYSTEMS_CONFIG.get(system_name)
    if not config:
        return None
    return {
        "name": system_name,
        "base_url": config["base_url"],
        "teacher_id": config["teacher_id"],
        "default_token": st.session_state.token_store.get(system_name, config["default_token"]),
    }


# ===== API调用 =====
def make_headers(token, system_name=None):
    if system_name == "entopia":
        return {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "domain": "app6.entopia.cn",
            "origin": "https://app6.entopia.cn",
            "referer": "https://app6.entopia.cn/",
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }
    return {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }


def simulate_login():
    """模拟entopia登录获取新token"""
    try:
        login_url = "https://api6.entopia.cn/appLogin"
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "domain": "app6.entopia.cn",
            "origin": "https://app6.entopia.cn",
            "referer": "https://app6.entopia.cn/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
        }
        payload = {
            "account": "044373f80733bfaa8a5e0bd3aba0f82c2e8be246af17f3784728be76463a2862a5f5f207259b598d80ed13d332308c0bbe805cc657488842231a84d46c4746ac7336462fd08d0fea38fe2aec98431201a93485e9e25db6d21f52413065f1ef3b1a9df7a096160380d37075",
            "hostname": "app6.entopia.cn",
            "password": "04f7871e9588d756aa7f744f12e95f2b3695e85398a7437efab89760869ad7dd0bcf82d9f169a9ba11783477313c17e34692c0774aeee1170c7c5316d6839583c2f940c24240c8dc1443421ff1881592123671c9459f1089aa50f7abcae96a060148ae3bb959fd",
        }
        resp = requests.post(login_url, json=payload, headers=headers, timeout=10)
        data = resp.json()
        if data.get("success") or data.get("code") == 200:
            token = data.get("authorization") or data.get("token") or data.get("access_token")
            if token:
                return token
            for key, val in data.items():
                if isinstance(val, str) and len(val) > 100 and val.startswith("ey"):
                    return val
        return None
    except Exception:
        return None


def auto_refresh_token(system_name):
    if system_name == "entopia":
        return simulate_login()
    return None


def fetch_courses(child_name, system_config, token):
    """获取当天课程"""
    headers = make_headers(token, system_config["name"])
    url = f"{system_config['base_url']}/record/statisticalTeacherClassRecord2"
    today = datetime.now()
    payload = {
        "teacherId": system_config["teacher_id"],
        "pageNum": 1,
        "pageSize": 50,
        "dataYear": today.year,
        "dataMonth": str(today.month).zfill(2),
    }

    add_log(f"正在获取当天课程数据...({system_config['name']}系统)")
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    add_log(f"状态码: {resp.status_code}")

    data = resp.json()
    if not data.get("success"):
        msg = data.get("message", "未知错误")
        if "登录失效" in str(msg):
            return None, "token_expired"
        return None, msg

    courses = data.get("page", {}).get("list", [])
    if not courses:
        add_log("API返回课程列表为空")
        return [], None

    add_log(f"共找到 {len(courses)} 条课程记录")
    child_courses = [c for c in courses if c.get("studentName") == child_name]
    if not child_courses:
        add_log(f"未找到 {child_name} 的课程记录")
        return [], None

    child_courses.sort(key=lambda x: x.get("beginTime", "") or str(x.get("aptmId", "")), reverse=True)
    add_log(f"已筛选出 {len(child_courses)} 条 {child_name} 的课程")
    for c in child_courses[:3]:
        add_log(f"  - {c.get('courseName', '')} (时间: {c.get('beginTime', '')})")

    return child_courses, None


def generate_feedback(child_name, system_config, token, course_data):
    """生成正课反馈"""
    if not course_data:
        return None, "没有课程数据，请先获取当天课程"

    latest = course_data[0]
    aptm_id = latest["aptmId"]
    course_name = latest.get("courseName", "")
    course_type_id = latest.get("courseTypeId", "")

    add_log(f"正在生成反馈: {child_name} (课程: {course_name})")
    headers = make_headers(token, system_config["name"])

    # 课程详情
    detail_url = f"{system_config['base_url']}/record/getClassRecordByAppointmentId?aptmId={aptm_id}"
    resp = requests.get(detail_url, headers=headers, timeout=30)
    detail_data = resp.json()
    if not detail_data.get("success"):
        msg = detail_data.get("message", "获取课程详情失败")
        if "登录失效" in str(msg):
            return None, "token_expired"
        return None, msg

    detail = detail_data.get("data") or {}
    begin_time = detail.get("beginTime", "")
    date_str = datetime.now().strftime("%Y年%m月%d日")
    if begin_time:
        try:
            date_str = datetime.strptime(begin_time[:10], "%Y-%m-%d").strftime("%Y年%m月%d日")
        except Exception:
            pass

    # 单词统计
    stats_url = f"{system_config['base_url']}/forgetSparring/findByClassInformation?aptmId={aptm_id}"
    add_log("获取单词统计...")
    resp = requests.get(stats_url, headers=headers, timeout=30)
    stats_data = resp.json()
    if not stats_data.get("success"):
        msg = stats_data.get("message", "获取单词统计失败")
        if "登录失效" in str(msg):
            return None, "token_expired"
        return None, msg

    stats = stats_data.get("data") or {}
    review_num = stats.get("reviewVocabularyNum") or 0
    new_num = stats.get("studyNewVocabularyNum") or 0
    review_forget = stats.get("reviewForget") or 0
    new_forget = stats.get("forgetNewVocabulary") or 0
    add_log(f"复习{review_num}个(遗忘{review_forget})，新学{new_num}个(遗忘{new_forget})")

    is_reading = "阅读" in course_name or "阅读" in str(course_type_id)
    feedback = f"用户：{child_name}\n陪练：武杰\n课程类型：{course_name}\n训练时间：{date_str}\n\n🌷课堂反馈🌷\n"

    if is_reading:
        feedback += "1.今日学习阅读2篇\n"
        feedback += f"2.今日新学单词{new_num}个，遗忘{new_forget}词\n"
        feedback += "3.习题10个，10正确\n"
    else:
        idx = 1
        if review_num > 0:
            feedback += f"{idx}.今日复习单词{review_num}个，遗忘{review_forget}词\n"
            idx += 1
        if new_num > 0:
            feedback += f"{idx}.今日新学单词{new_num}个，遗忘{new_forget}词\n"
            idx += 1
        today_learned = review_forget + new_num
        feedback += f"{idx}.今日已学{today_learned}词\n"

    feedback += "\n🌷陪练反馈🌷\n"
    add_log("正在生成AI个性化反馈...")
    generator = AIFeedbackGenerator()
    coach_feedback = generator.generate_coach_feedback(
        child_name, review_num, new_num, review_forget, new_forget,
        is_reading=is_reading, is_forget_training=False,
    )
    feedback += coach_feedback
    add_log("反馈生成完成!")
    return feedback, None


def fetch_forget_courses(child_name, system_config, token, student_id):
    """获取抗遗忘课程"""
    headers = make_headers(token, system_config["name"])
    url = f"{system_config['base_url']}/forgetSparring/findByPastReviewList"
    payload = {
        "studentId": student_id,
        "teacherId": system_config["teacher_id"],
        "pageNum": 1,
        "pageSize": 10,
    }

    add_log(f"正在获取抗遗忘课程数据...({system_config['name']}系统)")
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    add_log(f"状态码: {resp.status_code}")

    data = resp.json()
    if not data.get("success"):
        msg = data.get("message", "未知错误")
        if "登录失效" in str(msg):
            return None, "token_expired"
        return None, msg

    records = data.get("page", {}).get("list", [])
    if not records:
        add_log("没有找到抗遗忘课程记录")
        return [], None

    add_log(f"找到 {len(records)} 条抗遗忘课程记录")
    result = []
    for r in records:
        result.append({
            "reviewWords": r.get("reviewWords", 0),
            "scoreForgetNum": r.get("scoreForgetNum", 0),
            "scoreAccuracyNum": r.get("scoreAccuracyNum", 0),
            "accuracy": r.get("accuracy", 0),
            "forgetDate": r.get("forgetDate", ""),
            "teacherName": r.get("teacherName", ""),
        })

    latest = result[0]
    add_log(f"最新: 复习{latest['reviewWords']}个，遗忘{latest['scoreForgetNum']}个，正确率{int(latest['accuracy'] * 100)}%")
    return result, None


def generate_forget_feedback(child_name, forget_data):
    """生成抗遗忘反馈"""
    if not forget_data:
        return None, "没有抗遗忘课程数据，请先获取"

    latest = forget_data[0]
    review_words = latest.get("reviewWords", 0)
    score_forget = latest.get("scoreForgetNum", 0)
    score_accuracy = latest.get("scoreAccuracyNum", 0)
    accuracy = latest.get("accuracy", 0)
    forget_date = latest.get("forgetDate", "")
    teacher_name = latest.get("teacherName", "武杰")

    date_str = datetime.now().strftime("%Y年%m月%d日")
    if forget_date:
        try:
            date_str = datetime.strptime(forget_date[:10], "%Y-%m-%d").strftime("%Y年%m月%d日")
        except Exception:
            pass

    add_log(f"生成抗遗忘反馈: {child_name} (复习{review_words}个)")
    feedback = f"用户：{child_name}\n陪练：{teacher_name}\n课程类型：抗遗忘训练\n训练时间：{date_str}\n\n🌷课堂反馈🌷\n"
    feedback += f"1.今日复习单词{review_words}个，遗忘{score_forget}词\n"
    feedback += f"2.正确{score_accuracy}词，正确率{int(accuracy * 100)}%\n\n🌷陪练反馈🌷\n"

    add_log("正在生成AI个性化反馈...")
    generator = AIFeedbackGenerator()
    coach_feedback = generator.generate_coach_feedback(
        child_name, review_words, 0, score_forget, 0,
        is_reading=False, is_forget_training=True,
    )
    feedback += coach_feedback
    add_log("抗遗忘反馈生成完成!")
    return feedback, None


# ===== 页面 =====
st.set_page_config(page_title="课后反馈生成器", page_icon="📚", layout="wide")
init_state()

st.title("📚 课后反馈生成器")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")
    child = st.selectbox("选择学生", list(STUDENTS_CONFIG.keys()))
    student_info = STUDENTS_CONFIG.get(child, {})
    system_name = student_info.get("system", "")
    st.info(f"**系统**: {system_name}\n**学生ID**: {student_info.get('student_id', '')}")

    if TURSO_AVAILABLE:
        st.success("✅ Turso云数据库已连接")
    else:
        st.warning("⚠️ Turso未配置，使用默认配置")

    # Token管理
    with st.expander("🔑 Token管理"):
        token_system = st.selectbox("选择系统", ["yingxiaowu", "entopia"], key="token_system")
        new_token = st.text_area("新Token", key="new_token", height=80)
        if st.button("更新Token", use_container_width=True):
            if new_token.strip():
                st.session_state.token_store[token_system] = new_token.strip()
                if TURSO_AVAILABLE:
                    db = TursoDB()
                    db.save_token(token_system, new_token.strip())
                st.success(f"{token_system} Token已更新!")
                st.rerun()
            else:
                st.error("请输入Token")

# 操作按钮
st.subheader("操作")
col1, col2, col3, col4 = st.columns(4)
with col1:
    btn_fetch = st.button("📋 获取当天课程", use_container_width=True)
with col2:
    btn_feedback = st.button("✨ 生成反馈", use_container_width=True)
with col3:
    btn_forget = st.button("🔄 获取抗遗忘课程", use_container_width=True)
with col4:
    btn_forget_fb = st.button("📝 生成抗遗忘反馈", use_container_width=True)

# 状态日志
st.subheader("状态日志")
if st.session_state.logs:
    log_text = "\n".join(st.session_state.logs)
    st.code(log_text, language="text")
else:
    st.caption("等待操作...")

# 反馈结果
st.subheader("反馈结果")
if st.session_state.feedback:
    st.text_area("反馈内容", value=st.session_state.feedback, height=250, key="fb_display")
    st.code(st.session_state.feedback, language="text")
    st.caption("👆 点击右上角复制按钮可复制反馈内容")
else:
    st.info("生成的反馈将显示在这里...")

# ===== 按钮处理 =====
if btn_fetch:
    st.session_state.logs = []
    system_config = get_system_config(system_name)
    token = system_config["default_token"]

    with st.spinner("正在获取课程数据..."):
        courses, error = fetch_courses(child, system_config, token)
        if error == "token_expired":
            add_log("Token已失效，尝试自动刷新...")
            new_token = auto_refresh_token(system_name)
            if new_token:
                st.session_state.token_store[system_name] = new_token
                system_config["default_token"] = new_token
                add_log("Token刷新成功，重新获取...")
                courses, error = fetch_courses(child, system_config, new_token)

    if error:
        if error == "token_expired":
            add_log(f"Token已失效，请在侧边栏更新{system_name}系统Token")
        else:
            add_log(f"获取失败: {error}")
    else:
        st.session_state.course_data = courses
        st.session_state.course_data_child = child
        add_log(f"课程数据已保存，共{len(courses)}条")
    st.rerun()

if btn_feedback:
    st.session_state.logs = []
    if st.session_state.course_data_child != child or not st.session_state.course_data:
        add_log(f"请先获取 {child} 的当天课程")
    else:
        system_config = get_system_config(system_name)
        token = system_config["default_token"]

        with st.spinner("正在生成反馈..."):
            feedback, error = generate_feedback(child, system_config, token, st.session_state.course_data)
            if error == "token_expired":
                add_log("Token已失效，尝试自动刷新...")
                new_token = auto_refresh_token(system_name)
                if new_token:
                    st.session_state.token_store[system_name] = new_token
                    system_config["default_token"] = new_token
                    add_log("Token刷新成功，重新生成...")
                    feedback, error = generate_feedback(child, system_config, new_token, st.session_state.course_data)

        if error:
            if error == "token_expired":
                add_log(f"Token已失效，请在侧边栏更新{system_name}系统Token")
            else:
                add_log(f"生成失败: {error}")
        else:
            st.session_state.feedback = feedback
    st.rerun()

if btn_forget:
    st.session_state.logs = []
    system_config = get_system_config(system_name)
    token = system_config["default_token"]
    student_id = student_info.get("student_id", "")

    with st.spinner("正在获取抗遗忘课程数据..."):
        forget_data, error = fetch_forget_courses(child, system_config, token, student_id)
        if error == "token_expired":
            add_log("Token已失效，尝试自动刷新...")
            new_token = auto_refresh_token(system_name)
            if new_token:
                st.session_state.token_store[system_name] = new_token
                system_config["default_token"] = new_token
                add_log("Token刷新成功，重新获取...")
                forget_data, error = fetch_forget_courses(child, system_config, new_token, student_id)

    if error:
        if error == "token_expired":
            add_log(f"Token已失效，请在侧边栏更新{system_name}系统Token")
        else:
            add_log(f"获取失败: {error}")
    else:
        st.session_state.forget_course_data = forget_data
        st.session_state.forget_course_data_child = child
        add_log(f"抗遗忘数据已保存，共{len(forget_data)}条")
    st.rerun()

if btn_forget_fb:
    st.session_state.logs = []
    if st.session_state.forget_course_data_child != child or not st.session_state.forget_course_data:
        add_log(f"请先获取 {child} 的抗遗忘课程")
    else:
        with st.spinner("正在生成抗遗忘反馈..."):
            feedback, error = generate_forget_feedback(child, st.session_state.forget_course_data)

        if error:
            add_log(f"生成失败: {error}")
        else:
            st.session_state.feedback = feedback
    st.rerun()
