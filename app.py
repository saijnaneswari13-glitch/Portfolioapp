import streamlit as st
import html, re, base64, mimetypes
from io import BytesIO
from pathlib import Path
import zipfile

BASE = Path(__file__).parent
st.set_page_config(page_title="Resume to Portfolio", page_icon="✦", layout="wide")
template_path=BASE/"templates"/"portfolio.html"
html=template_path.read_text(encoding="utf-8")

st.markdown("""
<style>
.stApp{background:#050816}.block-container{max-width:1400px;padding-top:20px}
h1{background:linear-gradient(90deg,#fff,#00c6ff,#a855f7,#ec4899,#fff);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900}
.item{padding:12px;border:1px solid #24304a;border-radius:12px;background:#0b1225;margin:6px 0}
</style>
""", unsafe_allow_html=True)

def esc(x): return html.escape(str(x or ""), quote=True)

def normalize_url(x, kind):
    x = str(x or "").strip().replace(" ", "")
    if not x: return ""
    if kind == "github":
        x = re.sub(r"^https?://(www\.)?github\.com/", "", x, flags=re.I).strip("/")
        return "https://github.com/" + x
    if kind == "linkedin":
        x = re.sub(r"^https?://(www\.)?linkedin\.com/", "", x, flags=re.I).strip("/")
        if not x.startswith("in/"): x = "in/" + x
        return "https://www.linkedin.com/" + x
    return x if re.match(r"^https?://", x, re.I) else "https://" + x

def image_data(f):
    if not f: return ""
    mime=f.type or mimetypes.guess_type(f.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(f.getvalue()).decode()}"

def stars(n):
    n=int(n)
    return "★"*n+"☆"*(5-n)

def make_skills(items):
    return "".join(
        f'<div class="skill-card"><div><b>{esc(s["name"])}</b>'
        f'<span class="rating">{stars(s["rating"])}</span></div>'
        f'<small>{s["rating"]}/5</small></div>' for s in items
    ) or "<p>No skills added.</p>"

def make_education(items):
    return "".join(
        f'<div class="edu-card"><span>{esc(e["level"])}</span><h3>{esc(e["course"])}</h3>'
        f'<p>{esc(e["institution"])}</p><p>{esc(e["year"])} · {esc(e["score"])}</p></div>'
        for e in items
    ) or "<p>No education added.</p>"

def make_certs(items):
    result=[]
    for i,c in enumerate(items,1):
        photo=f'<img src="{c["image"]}" alt="Certificate">' if c["image"] else '<div class="no-photo">No photo</div>'
        result.append(
            f'<div class="cert-card"><div class="cert-photo">{photo}</div>'
            f'<span>CERTIFICATE {i:02d}</span><h3>{esc(c["name"])}</h3>'
            f'<p>{esc(c["issuer"])} · {esc(c["date"])}</p></div>'
        )
    return "".join(result) or "<p>No certificates added.</p>"

def generate(d):
    t=(BASE/"templates"/"portfolio.html").read_text()
    css=(BASE/"static"/"style.css").read_text()
    js=(BASE/"static"/"script.js").read_text()
    vals={
      "{{NAME}}":esc(d["name"]), "{{TITLE}}":esc(d["title"]), "{{EMAIL}}":esc(d["email"]),
      "{{PHONE}}":esc(d["phone"]), "{{LOCATION}}":esc(d["location"]),
      "{{OBJECTIVE}}":esc(d["objective"]), "{{SKILLS}}":make_skills(d["skills"]),
      "{{EDUCATION}}":make_education(d["education"]), "{{CERTIFICATES}}":make_certs(d["certificates"]),
      "{{LINKEDIN}}":esc(normalize_url(d["linkedin"],"linkedin")),
      "{{GITHUB}}":esc(normalize_url(d["github"],"github"))
    }
    for k,v in vals.items(): t=t.replace(k,v)
    return t.replace('<link rel="stylesheet" href="../static/style.css">',f"<style>{css}</style>").replace(
        '<script src="../static/script.js"></script>',f"<script>{js}</script>")

for k in ("skills","education","certificates"):
    if k not in st.session_state: st.session_state[k]=[]

st.title("✦ Resume to Portfolio")
st.caption("Dynamic portfolio builder")

st.subheader("Personal Details")
a,b=st.columns(2)
with a:
    name=st.text_input("Full Name")
    title=st.text_input("Professional Title","Software Developer")
    email=st.text_input("Email")
    phone=st.text_input("Phone")
with b:
    location=st.text_input("Location")
    linkedin=st.text_input("LinkedIn",placeholder="linkedin.com/in/yourname")
    github=st.text_input("GitHub",placeholder="github.com/yourname")

st.subheader("🎯 Objective")
objective=st.text_area("Career Objective",height=120,placeholder="Write your career objective...")

st.subheader("⭐ Skills — Add as many as you want")
a,b,c=st.columns([2,1,1])
with a: sn=st.text_input("Skill name",placeholder="Python")
with b: sr=st.selectbox("Star rating",[1,2,3,4,5],index=4)
with c:
    st.write("")
    if st.button("＋ Add Skill"):
        if sn.strip():
            st.session_state.skills.append({"name":sn.strip(),"rating":sr})
            st.rerun()
for i,s in enumerate(st.session_state.skills):
    x,y=st.columns([4,1]); x.markdown(f'<div class="item"><b>{esc(s["name"])}</b> &nbsp; <span style="color:#ffc83d">{stars(s["rating"])}</span></div>',unsafe_allow_html=True)
    if y.button("Remove",key=f"rs{i}"): st.session_state.skills.pop(i); st.rerun()

st.subheader("🎓 Education — Add 10th, Intermediate, Diploma, B.Tech...")
a,b=st.columns(2)
with a:
    level=st.selectbox("Education",["10th","Intermediate","Diploma","B.Tech","Other"])
    course=st.text_input("Course / Branch",placeholder="CSE / AI & ML")
    institution=st.text_input("School / College")
with b:
    year=st.text_input("Year",placeholder="2026")
    score=st.text_input("Percentage / CGPA",placeholder="85% / 8.2")
    if st.button("＋ Add Education"):
        if institution.strip() or course.strip():
            st.session_state.education.append({"level":level,"course":course,"institution":institution,"year":year,"score":score})
            st.rerun()
for i,e in enumerate(st.session_state.education):
    x,y=st.columns([5,1])
    x.markdown(f'<div class="item"><b>{esc(e["level"])}</b> — {esc(e["course"])} | {esc(e["institution"])} | {esc(e["year"])} | {esc(e["score"])}</div>',unsafe_allow_html=True)
    if y.button("Remove",key=f"re{i}"): st.session_state.education.pop(i); st.rerun()

st.subheader("📜 Certificates — Add multiple certificates")
a,b=st.columns(2)
with a:
    cn=st.text_input("Certificate Name",placeholder="Python Certificate")
    ci=st.text_input("Issued By",placeholder="Microsoft / Coursera")
with b:
    cd=st.text_input("Certificate Date",placeholder="August 2026")
    cp=st.file_uploader("📷 Certificate Photo",type=["png","jpg","jpeg","webp"],key="certificate_photo")
if cp: st.image(cp,width=260)
if st.button("＋ Add Certificate"):
    if cn.strip():
        st.session_state.certificates.append({"name":cn,"issuer":ci,"date":cd,"image":image_data(cp)})
        st.rerun()
for i,c in enumerate(st.session_state.certificates):
    x,y=st.columns([5,1])
    x.markdown(f'<div class="item"><b>{i+1}. {esc(c["name"])}</b> — {esc(c["issuer"])} — {esc(c["date"])}</div>',unsafe_allow_html=True)
    if y.button("Remove",key=f"rc{i}"): st.session_state.certificates.pop(i); st.rerun()

if st.button("✦ Generate Portfolio",type="primary",use_container_width=True):
    if not name.strip(): st.error("Please enter your name.")
    else:
        st.session_state.data={"name":name,"title":title,"email":email,"phone":phone,"location":location,
        "linkedin":linkedin,"github":github,"objective":objective,"skills":st.session_state.skills.copy(),
        "education":st.session_state.education.copy(),"certificates":st.session_state.certificates.copy()}
        st.success("Portfolio generated successfully.")

if "data" in st.session_state:
    st.subheader("🌐 Portfolio Preview")
    out=generate(st.session_state.data)
    st.components.v1.html(out,height=3000,scrolling=True)
    st.download_button("⬇ Download Portfolio HTML",out,"portfolio.html","text/html",use_container_width=True)
    z=BytesIO()
    with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as f: f.writestr("portfolio.html",out)
    z.seek(0)
    st.download_button("📦 Download ZIP",z,"portfolio.zip","application/zip",use_container_width=True)
