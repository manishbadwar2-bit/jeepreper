import os,sqlite3
from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory,flash
from werkzeug.utils import secure_filename
BASE=os.path.dirname(os.path.abspath(__file__)); DB=os.path.join(BASE,"site.db"); UP=os.path.join(BASE,"uploads")
os.makedirs(UP,exist_ok=True)
app=Flask(__name__); app.secret_key=os.environ.get("SECRET_KEY","change-this-secret")
USER=os.environ.get("ADMIN_USER","Manish"); PASS=os.environ.get("ADMIN_PASS","Manish@95184")
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 c=db(); c.executescript("""CREATE TABLE IF NOT EXISTS materials(id INTEGER PRIMARY KEY,title TEXT,subject TEXT,description TEXT,filename TEXT);
CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY,title TEXT,description TEXT,pay TEXT);
CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY,name TEXT,price TEXT,description TEXT);"""); c.commit(); c.close()
@app.context_processor
def ctx(): return {"logged_in":session.get("admin")}
@app.route("/")
def home():
 c=db(); m=c.execute("SELECT * FROM materials ORDER BY id DESC").fetchall(); j=c.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall(); p=c.execute("SELECT * FROM plans ORDER BY id DESC").fetchall(); c.close()
 return render_template("index.html",materials=m,jobs=j,plans=p)
@app.route("/login",methods=["GET","POST"])
def login():
 if request.method=="POST":
  if request.form["username"]==USER and request.form["password"]==PASS: session["admin"]=1; return redirect("/admin")
  flash("Wrong login")
 return render_template("login.html")
@app.route("/logout")
def logout(): session.clear(); return redirect("/")
def ok(): return session.get("admin")
@app.route("/admin")
def admin():
 if not ok(): return redirect("/login")
 c=db(); m=c.execute("SELECT * FROM materials ORDER BY id DESC").fetchall(); j=c.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall(); p=c.execute("SELECT * FROM plans ORDER BY id DESC").fetchall(); c.close()
 return render_template("admin.html",materials=m,jobs=j,plans=p)
@app.route("/admin/material/add",methods=["POST"])
def mat_add():
 if not ok(): return redirect("/login")
 f=request.files["file"]; name=secure_filename(f.filename); base,ext=os.path.splitext(name); i=1
 while os.path.exists(os.path.join(UP,name)): name=f"{base}_{i}{ext}"; i+=1
 f.save(os.path.join(UP,name)); c=db(); c.execute("INSERT INTO materials(title,subject,description,filename) VALUES(?,?,?,?)",(request.form["title"],request.form["subject"],request.form.get("description",""),name)); c.commit(); c.close(); return redirect("/admin")
@app.route("/admin/material/delete/<int:i>",methods=["POST"])
def mat_del(i):
 if not ok(): return redirect("/login")
 c=db(); r=c.execute("SELECT filename FROM materials WHERE id=?",(i,)).fetchone()
 if r and os.path.exists(os.path.join(UP,r["filename"])): os.remove(os.path.join(UP,r["filename"]))
 c.execute("DELETE FROM materials WHERE id=?",(i,)); c.commit(); c.close(); return redirect("/admin")
@app.route("/admin/job/add",methods=["POST"])
def job_add():
 if not ok(): return redirect("/login")
 c=db(); c.execute("INSERT INTO jobs(title,description,pay) VALUES(?,?,?)",(request.form["title"],request.form.get("description",""),request.form.get("pay",""))); c.commit(); c.close(); return redirect("/admin")
@app.route("/admin/job/delete/<int:i>",methods=["POST"])
def job_del(i):
 if not ok(): return redirect("/login")
 c=db(); c.execute("DELETE FROM jobs WHERE id=?",(i,)); c.commit(); c.close(); return redirect("/admin")
@app.route("/admin/plan/add",methods=["POST"])
def plan_add():
 if not ok(): return redirect("/login")
 c=db(); c.execute("INSERT INTO plans(name,price,description) VALUES(?,?,?)",(request.form["name"],request.form["price"],request.form.get("description",""))); c.commit(); c.close(); return redirect("/admin")
@app.route("/admin/plan/delete/<int:i>",methods=["POST"])
def plan_del(i):
 if not ok(): return redirect("/login")
 c=db(); c.execute("DELETE FROM plans WHERE id=?",(i,)); c.commit(); c.close(); return redirect("/admin")
@app.route("/files/<path:n>")
def files(n): return send_from_directory(UP,n,as_attachment=True)
if __name__=="__main__": init(); app.run(host="127.0.0.1",port=5000,debug=True)
