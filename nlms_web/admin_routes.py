# admin_routes.py
from flask import request, render_template, session, redirect, flash, url_for
from db_config import get_db_connection
import math

def register_admin(app):
    @app.route("/books")
    def books():
        if session.get("user_role") != "admin":
            return redirect("/login")

        q    = request.args.get("q", "").strip()
        sort = request.args.get("sort", "title")
        page = int(request.args.get("page", 1))
        per_page = 10

        conn = get_db_connection()
        cur  = conn.cursor()

        where_clauses, params = [], []
        if q:
            likeq = f"%{q}%"
            where_clauses.append(
                "(b.title LIKE %s OR b.isbn LIKE %s OR CONCAT(a.first_name,' ',a.last_name) LIKE %s)"
            )
            params += [likeq, likeq, likeq]
        where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        cur.execute(f"""
            SELECT COUNT(DISTINCT b.book_id)
            FROM Books b
            JOIN BookAuthors ba ON b.book_id=ba.book_id
            JOIN Authors a ON ba.author_id=a.author_id
            {where}
        """, params)
        total = cur.fetchone()[0]
        total_pages = max(1, math.ceil(total / per_page))
        offset = (page - 1) * per_page

        cur.execute(f"""
            SELECT b.book_id, b.title, b.isbn, b.publication_year,
                   GROUP_CONCAT(CONCAT(a.first_name,' ',a.last_name) SEPARATOR ', ') AS authors
            FROM Books b
            JOIN BookAuthors ba ON b.book_id=ba.book_id
            JOIN Authors a ON ba.author_id=a.author_id
            {where}
            GROUP BY b.book_id, b.title, b.isbn, b.publication_year
            ORDER BY {sort} ASC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        books = cur.fetchall()
        conn.close()

        start = max(1, page - 3)
        end   = min(total_pages, page + 3)
        window = list(range(start, end + 1))

        return render_template(
            "home.html",
            books=books,
            q=q,
            sort=sort,
            page=page,
            total_pages=total_pages,
            page_window=window,
            user_role="admin",
            user_name=session["user_name"]
        )

    @app.route("/manage-users")
    def manage_users():
        if session.get("user_role") != "admin":
            return redirect("/login")

        # 分页参数
        page = int(request.args.get("page", 1))
        per_page = 10
        offset = (page - 1) * per_page

        conn = get_db_connection()
        cur = conn.cursor()

        # 用户总数
        cur.execute("SELECT COUNT(*) FROM Users")
        total = cur.fetchone()[0]
        total_pages = max(1, math.ceil(total / per_page))

        # 查询用户列表（按 user_id 倒序）
        cur.execute("""
            SELECT user_id,
                   name,
                   email,
                   phone,
                   role
            FROM Users
            ORDER BY user_id DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        users = cur.fetchall()
        conn.close()

        # 计算分页窗口
        start = max(1, page - 3)
        end   = min(total_pages, page + 3)
        window = list(range(start, end + 1))

        return render_template(
            "manage_users.html",
            users=users,
            page=page,
            total_pages=total_pages,
            page_window=window,
            user_role="admin",
            user_name=session["user_name"]
        )
    @app.route("/delete-user/<int:user_id>")
    @app.route("/edit-user/<int:user_id>", methods=["GET", "POST"])
    def edit_user(user_id):
        # 仅限 admin
        if session.get("user_role") != "admin":
            flash("Only admins can edit users.", "error")
            return redirect(url_for("manage_users"))

        conn = get_db_connection()
        cur = conn.cursor()

        # GET：读取当前信息，渲染表单
        if request.method == "GET":
            cur.execute("""
                SELECT user_id, name, email, phone, role
                FROM Users
                WHERE user_id=%s
            """, (user_id,))
            user = cur.fetchone()
            conn.close()
            if not user:
                flash("User not found.", "error")
                return redirect(url_for("manage_users"))

            return render_template("edit_user.html", user=user)

        # POST：处理表单提交，更新数据库
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        role  = request.form.get("role")

        # 简单校验
        if not name or not email or role not in ("student","teacher","regular","admin"):
            flash("Please fill in all fields correctly.", "error")
            return redirect(url_for("edit_user", user_id=user_id))

        # 不允许修改其他管理员为非 admin，或自己降级
        if user_id == session.get("user_id") and role != "admin":
            flash("You cannot change your own admin role.", "error")
            return redirect(url_for("edit_user", user_id=user_id))

        # 更新
        try:
            cur.execute("""
                UPDATE Users
                SET name=%s, email=%s, phone=%s, role=%s
                WHERE user_id=%s
            """, (name, email, phone, role, user_id))
            conn.commit()
            flash("User updated.", "success")
        except Exception as e:
            conn.rollback()
            flash("Error updating user: " + str(e), "error")
        finally:
            conn.close()

        return redirect(url_for("manage_users"))    
    
    @app.route("/add-book", methods=["GET", "POST"])
    def add_book():
        if session.get("user_role") != "admin":
            flash("Only admins can add books.", "error")
            return redirect(url_for("books"))

        conn = get_db_connection()
        cur = conn.cursor()

        if request.method == "GET":
            # 获取所有分类和作者
            cur.execute("SELECT category_id, name FROM Categories")
            categories = cur.fetchall()
            cur.execute("SELECT author_id, CONCAT(first_name,' ',last_name) FROM Authors")
            authors = cur.fetchall()
            conn.close()
            return render_template("add_book.html",
                                   categories=categories,
                                   authors=authors)

        # POST：处理表单
        title        = request.form.get("title", "").strip()
        isbn         = request.form.get("isbn", "").strip()
        publisher    = request.form.get("publisher", "").strip()
        year         = request.form.get("year", "").strip()
        sel_category = request.form.get("category")
        new_category = request.form.get("new_category", "").strip()
        sel_authors  = request.form.getlist("authors")
        new_authors_first = request.form.get("new_authors_first", "").strip().splitlines()
        new_authors_last  = request.form.get("new_authors_last", "").strip().splitlines()

        # 基本校验
        if not title or not isbn or not publisher or not year.isdigit():
            flash("Please fill in title, ISBN, publisher, and year correctly.", "error")
            return redirect(url_for("add_book"))

        try:
            # 1. 处理分类
            if new_category:
                cur.execute("INSERT INTO Categories (name) VALUES (%s)", (new_category,))
                category_id = cur.lastrowid
            else:
                category_id = int(sel_category)

            # 2. 插入 Books
            cur.execute("""
                INSERT INTO Books (title, isbn, publisher, publication_year, category_id)
                VALUES (%s,%s,%s,%s,%s)
            """, (title, isbn, publisher, int(year), category_id))
            book_id = cur.lastrowid

            # 3. 处理作者列表
            author_ids = [int(aid) for aid in sel_authors]

            # 新作者：按行对应 first/last
            for fn, ln in zip(new_authors_first, new_authors_last):
                fn = fn.strip()
                ln = ln.strip()
                if not fn or not ln:
                    continue
                cur.execute(
                    "INSERT INTO Authors (first_name, last_name) VALUES (%s,%s)",
                    (fn, ln)
                )
                author_ids.append(cur.lastrowid)

            # 4. 插入 BookAuthors
            for aid in author_ids:
                cur.execute(
                    "INSERT INTO BookAuthors (book_id, author_id) VALUES (%s,%s)",
                    (book_id, aid)
                )

            conn.commit()
            flash("Book added successfully.", "success")
        except Exception as e:
            conn.rollback()
            flash("Error adding book: " + str(e), "error")
        finally:
            conn.close()

        return redirect(url_for("books"))
        if session.get("user_role") != "admin":
            flash("Only admins can add books.", "error")
            return redirect(url_for("books"))

        conn = get_db_connection()
        cur = conn.cursor()

        if request.method == "GET":
            cur.execute("SELECT category_id, name FROM Categories")
            categories = cur.fetchall()
            cur.execute("SELECT author_id, CONCAT(first_name,' ',last_name) FROM Authors")
            authors = cur.fetchall()
            conn.close()
            return render_template("add_book.html",
                                   categories=categories,
                                   authors=authors)

        # POST
        title        = request.form.get("title","").strip()
        isbn         = request.form.get("isbn","").strip()
        publisher    = request.form.get("publisher","").strip()
        year         = request.form.get("year","").strip()
        sel_category = request.form.get("category")
        new_category = request.form.get("new_category","").strip()
        sel_authors  = request.form.getlist("authors")
        new_authors  = request.form.get("new_authors","").strip()

        if not title or not isbn or not publisher or not year.isdigit():
            flash("Please fill in title, ISBN, publisher, and year correctly.", "error")
            return redirect(url_for("add_book"))

        try:
            # 1. 处理分类：如果 new_category 非空，插入并取回 id；否则用 sel_category
            if new_category:
                cur.execute("INSERT INTO Categories (name) VALUES (%s)", (new_category,))
                category_id = cur.lastrowid
            else:
                category_id = int(sel_category)

            # 2. 插入 Books
            cur.execute("""
                INSERT INTO Books (title, isbn, publisher, publication_year, category_id)
                VALUES (%s,%s,%s,%s,%s)
            """, (title, isbn, publisher, int(year), category_id))
            book_id = cur.lastrowid

            # 3. 处理作者列表
            author_ids = []

            # 已选作者
            for aid in sel_authors:
                author_ids.append(int(aid))

            # 新输入作者，用逗号分隔
            if new_authors:
                # 格式："First Last, Another Author"
                for name in new_authors.split(","):
                    name = name.strip()
                    if not name: continue
                    parts = name.split()
                    first = parts[0]
                    last  = " ".join(parts[1:]) if len(parts)>1 else ""
                    cur.execute("""
                        INSERT INTO Authors (first_name, last_name)
                        VALUES (%s,%s)
                    """, (first, last))
                    author_ids.append(cur.lastrowid)

            # 4. 插入 BookAuthors
            for aid in author_ids:
                cur.execute("INSERT INTO BookAuthors (book_id,author_id) VALUES (%s,%s)",
                            (book_id, aid))

            conn.commit()
            flash("Book added successfully.", "success")
        except Exception as e:
            conn.rollback()
            flash("Error adding book: " + str(e), "error")
        finally:
            conn.close()

        return redirect(url_for("books"))
        if session.get("user_role") != "admin":
            flash("Only admins can add books.", "error")
            return redirect(url_for("books"))

        conn = get_db_connection()
        cur = conn.cursor()

        if request.method == "GET":
            # 取出所有分类和作者，供下拉/多选
            cur.execute("SELECT category_id, name FROM Categories")
            categories = cur.fetchall()
            cur.execute("SELECT author_id, CONCAT(first_name,' ',last_name) FROM Authors")
            authors = cur.fetchall()
            conn.close()
            return render_template("add_book.html",
                                   categories=categories,
                                   authors=authors)

        # POST：处理表单提交
        title     = request.form.get("title", "").strip()
        isbn      = request.form.get("isbn", "").strip()
        publisher = request.form.get("publisher", "").strip()
        year      = request.form.get("year", "").strip()
        category  = request.form.get("category")
        author_ids = request.form.getlist("authors")  # 多选

        # 简单校验
        if not title or not isbn or not publisher or not year.isdigit() or not category:
            flash("Please fill in all required fields correctly.", "error")
            return redirect(url_for("add_book"))

        try:
            # 插入 Books
            cur.execute("""
                INSERT INTO Books (title, isbn, publisher, publication_year, category_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, isbn, publisher, int(year), int(category)))
            book_id = cur.lastrowid

            # 插入 BookAuthors
            for aid in author_ids:
                cur.execute("""
                    INSERT INTO BookAuthors (book_id, author_id)
                    VALUES (%s, %s)
                """, (book_id, int(aid)))

            conn.commit()
            flash("Book added successfully.", "success")
        except Exception as e:
            conn.rollback()
            flash("Error adding book: " + str(e), "error")
        finally:
            conn.close()

        return redirect(url_for("books"))