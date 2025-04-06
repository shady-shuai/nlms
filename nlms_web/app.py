# from flask import Flask, render_template, request, redirect, session, flash
# from db_config import get_db_connection
# import math
# from datetime import date, timedelta

# app = Flask(__name__)
# app.secret_key = 'group8'

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     error = None
#     if request.method == "POST":
#         email = request.form["email"].strip()
#         password = request.form["password"].strip()

#         conn = get_db_connection()
#         cur = conn.cursor(dictionary=True)
#         cur.execute("SELECT * FROM Users WHERE email=%s", (email,))
#         user = cur.fetchone()
#         conn.close()

#         if not user or user["password"] != password:
#             error = "Invalid email or password."
#         else:
#             session["user_id"]   = user["user_id"]
#             session["user_name"] = user["name"]
#             session["user_role"] = user["role"]
#             if user["role"] == "admin":
#                 return redirect("/books")
#             else:
#                 return redirect("/copies")
#     return render_template("login.html", error=error)

# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/login")

# @app.route("/")
# def index():
#     role = session.get("user_role")
#     if not role:
#         return redirect("/login")
#     return redirect("/books") if role == "admin" else redirect("/copies")

# @app.route("/books")
# def books():
#     if session.get("user_role") != "admin":
#         return redirect("/login")
#     # 这里保持原有 home.html 渲染逻辑
#     # 省略查询细节，只示意
#     return render_template("home.html",
#         books=[], q="", sort="title", page=1,
#         total_pages=1, page_window=[1],
#         user_role="admin", user_name=session["user_name"]
#     )

# @app.route("/copies")
# def list_copies():
#     if not session.get("user_role"):
#         return redirect("/login")

#     user_id   = session["user_id"]
#     user_role = session["user_role"]

#     q           = request.args.get("q", "").strip()
#     branch_id   = request.args.get("branch_id", "").strip()
#     page        = int(request.args.get("page", 1))
#     per_page    = 10

#     conn = get_db_connection()
#     cur  = conn.cursor()

#     # 分馆列表
#     cur.execute("SELECT branch_id, branch_name FROM LibraryBranches")
#     branches = cur.fetchall()

#     # 构造 WHERE
#     wheres, params = [], []
#     if q:
#         wheres.append("(b.title LIKE %s OR b.isbn LIKE %s)")
#         likeq = f"%{q}%"
#         params += [likeq, likeq]
#     if branch_id:
#         wheres.append("bc.branch_id = %s")
#         params.append(branch_id)
#     where_clause = "WHERE " + " AND ".join(wheres) if wheres else ""

#     # 统计总数
#     cur.execute(f"""
#       SELECT COUNT(*) FROM BookCopies bc
#       JOIN Books b ON bc.book_id = b.book_id
#       {where_clause}
#     """, params)
#     total = cur.fetchone()[0]
#     total_pages = max(1, math.ceil(total / per_page))
#     offset = (page - 1) * per_page

#     # 查询数据
#     cur.execute(f"""
#       SELECT
#         bc.copy_id,
#         b.title,
#         b.isbn,
#         bc.status,
#         COALESCE(lb.branch_name, 'Unknown') AS branch_name
#       FROM BookCopies bc
#       JOIN Books b  ON bc.book_id = b.book_id
#       LEFT JOIN LibraryBranches lb ON bc.branch_id = lb.branch_id
#       {where_clause}
#       ORDER BY b.title ASC
#       LIMIT %s OFFSET %s
#     """, params + [per_page, offset])
#     copies = cur.fetchall()

#     # 计算页码窗口
#     start_page = max(1, page - 3)
#     end_page   = min(total_pages, page + 3)
#     page_window = list(range(start_page, end_page + 1))

#     # 普通用户已借集合
#     borrowed = set()
#     if user_role != "admin":
#         cur.execute("""
#           SELECT copy_id FROM BorrowingRecords
#           WHERE user_id=%s AND return_date IS NULL
#         """, (user_id,))
#         borrowed = {r[0] for r in cur.fetchall()}

#     conn.close()

#     return render_template("copies.html",
#         copies=copies,
#         branches=branches,
#         selected_branch=branch_id,
#         q=q,
#         page=page,
#         total_pages=total_pages,
#         page_window=page_window,
#         user_role=user_role,
#         user_name=session["user_name"],
#         borrowed=borrowed
#     )

# @app.route("/borrow/<int:copy_id>")
# def borrow(copy_id):
#     if session.get("user_role") == "admin":
#         flash("Admins cannot borrow books.", "error")
#     else:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT status FROM BookCopies WHERE copy_id=%s", (copy_id,))
#         status = cur.fetchone()[0]
#         if status != "available":
#             flash("This copy is not available.", "error")
#         else:
#             due = date.today() + timedelta(days=14)
#             cur.execute("""
#               INSERT INTO BorrowingRecords(user_id, copy_id, borrow_date, due_date)
#               VALUES(%s, %s, CURDATE(), %s)
#             """, (session["user_id"], copy_id, due))
#             cur.execute("UPDATE BookCopies SET status='borrowed' WHERE copy_id=%s", (copy_id,))
#             conn.commit()
#             flash("Book borrowed successfully.", "success")
#         conn.close()
#     return redirect("/copies")

# @app.route("/return/<int:copy_id>")
# def ret(copy_id):
#     if session.get("user_role") == "admin":
#         flash("Admins cannot return books.", "error")
#     else:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("""
#           UPDATE BorrowingRecords
#           SET return_date=CURDATE()
#           WHERE user_id=%s AND copy_id=%s AND return_date IS NULL
#         """, (session["user_id"], copy_id))
#         cur.execute("UPDATE BookCopies SET status='available' WHERE copy_id=%s", (copy_id,))
#         conn.commit()
#         conn.close()
#         flash("Book returned successfully.", "success")
#     return redirect("/copies")

# @app.route("/delete/<int:copy_id>")
# def delete(copy_id):
#     if session.get("user_role") != "admin":
#         flash("Only admins can delete copies.", "error")
#     else:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("DELETE FROM BookCopies WHERE copy_id=%s", (copy_id,))
#         conn.commit()
#         conn.close()
#         flash("Copy deleted.", "success")
#     return redirect("/copies")

# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask
from db_config import get_db_connection  # 只要有这个文件
import auth, admin_routes, user_routes

app = Flask(__name__)
app.secret_key = 'group8'

# 注册各模块的路由
auth.register_auth(app)
admin_routes.register_admin(app)
user_routes.register_user(app)

if __name__ == "__main__":
    app.run(debug=True)
