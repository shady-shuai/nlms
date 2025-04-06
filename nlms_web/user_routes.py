from flask import request, render_template, session, redirect, flash
from db_config import get_db_connection
import math
from datetime import date, timedelta

def register_user(app):
    @app.route("/copies")
    def copies():
        if not session.get("user_role"):
            return redirect("/login")

        user_id   = session["user_id"]
        user_role = session["user_role"]

        q         = request.args.get("q","").strip()
        branch_id = request.args.get("branch_id","").strip()
        page      = int(request.args.get("page",1))
        per_page  = 10

        conn = get_db_connection()
        cur  = conn.cursor()

        cur.execute("SELECT branch_id, branch_name FROM LibraryBranches")
        branches = cur.fetchall()

        wheres, params = [], []
        if q:
            wheres.append("(b.title LIKE %s OR b.isbn LIKE %s)")
            likeq = f"%{q}%"
            params += [likeq, likeq]
        if branch_id:
            wheres.append("bc.branch_id = %s")
            params.append(branch_id)
        where_clause = "WHERE " + " AND ".join(wheres) if wheres else ""

        cur.execute(f"""
          SELECT COUNT(*) FROM BookCopies bc
          JOIN Books b ON bc.book_id=b.book_id
          {where_clause}
        """, params)
        total = cur.fetchone()[0]
        total_pages = max(1, math.ceil(total/per_page))
        offset = (page-1)*per_page

        cur.execute(f"""
          SELECT bc.copy_id, b.title, b.isbn, bc.status,
                 COALESCE(lb.branch_name,'Unknown')
          FROM BookCopies bc
          JOIN Books b ON bc.book_id=b.book_id
          LEFT JOIN LibraryBranches lb ON bc.branch_id=lb.branch_id
          {where_clause}
          ORDER BY b.title ASC
          LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        copies = cur.fetchall()

        start = max(1, page-3)
        end   = min(total_pages, page+3)
        window = list(range(start, end+1))

        borrowed = set()
        if user_role!="admin":
            cur.execute("SELECT copy_id FROM BorrowingRecords WHERE user_id=%s AND return_date IS NULL",(user_id,))
            borrowed = {r[0] for r in cur.fetchall()}

        conn.close()

        return render_template("copies.html",
            copies=copies, branches=branches, selected_branch=branch_id,
            q=q, page=page, total_pages=total_pages, page_window=window,
            user_role=user_role, user_name=session["user_name"], borrowed=borrowed
        )

    @app.route("/copies/borrow/<int:copy_id>")
    def borrow(copy_id):
        if session.get("user_role")=="admin":
            flash("Admins cannot borrow.","error")
        else:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT status FROM BookCopies WHERE copy_id=%s",(copy_id,))
            if cur.fetchone()[0]!="available":
                flash("Not available","error")
            else:
                due = date.today()+timedelta(days=14)
                cur.execute("INSERT INTO BorrowingRecords(user_id,copy_id,borrow_date,due_date) VALUES(%s,%s,CURDATE(),%s)",
                            (session["user_id"],copy_id,due))
                cur.execute("UPDATE BookCopies SET status='borrowed' WHERE copy_id=%s",(copy_id,))
                conn.commit(); flash("Borrowed","success")
            conn.close()
        return redirect("/copies")

    @app.route("/copies/return/<int:copy_id>")
    def ret(copy_id):
        if session.get("user_role")=="admin":
            flash("Admins cannot return.","error")
        else:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("UPDATE BorrowingRecords SET return_date=CURDATE() WHERE user_id=%s AND copy_id=%s AND return_date IS NULL",
                        (session["user_id"],copy_id))
            cur.execute("UPDATE BookCopies SET status='available' WHERE copy_id=%s",(copy_id,))
            conn.commit(); conn.close(); flash("Returned","success")
        return redirect("/copies")

    @app.route("/copies/delete/<int:copy_id>")
    def delete(copy_id):
        if session.get("user_role")!="admin":
            flash("Only admins","error")
        else:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM BookCopies WHERE copy_id=%s",(copy_id,))
            conn.commit(); conn.close(); flash("Deleted","success")
        return redirect("/copies")

    @app.route("/my-borrowings")
    def my_borrowings():
        if not session.get("user_role") or session.get("user_role")=="admin":
            return redirect("/login")
        user_id = session["user_id"]
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
          SELECT br.copy_id, b.title, b.isbn, br.borrow_date, br.due_date, br.return_date
          FROM BorrowingRecords br
          JOIN BookCopies bc ON br.copy_id=bc.copy_id
          JOIN Books b ON bc.book_id=b.book_id
          WHERE br.user_id=%s
          ORDER BY br.borrow_date DESC
        """, (user_id,))
        records = cur.fetchall()
        conn.close()
        return render_template("my_borrowings.html", records=records, user_name=session["user_name"])
    