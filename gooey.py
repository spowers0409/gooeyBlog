import tkinter as tk
from tkinter import messagebox, scrolledtext
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import webbrowser
import pytz
from datetime import datetime

# Create the sqlalchemy base setup
Base = declarative_base()

# Needing to update to show correct time
central_time = pytz.timezone('America/Chicago')

# Create the user information. Needs to have an id, author, and an email
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    author = Column(String, unique=True, nullable=False)
    
    posts = relationship('Post', back_populates='author')
    
    def __repr__(self):
        return f"<User(author={self.author})>"

# Create Post to store information about each blog post
class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    publication_date = Column(DateTime, default=lambda: datetime.now(central_time))
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    author = relationship('User', back_populates='posts')
    
    def __repr__(self):
        return f"<Post(title={self.title}, author_id={self.author_id})>"

# Create the database session for backendBlog.db
engine = create_engine('sqlite:///backendBlog.db')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

# *added new* function to allow tab movement between text boxes
def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break" 

# Create a function that enables a user to CREATE a new blog post    
def create_post():
    title = title_entry.get()
    content = content_text.get("1.0", tk.END)
    author_name = author_entry.get()

    if title and content and author_name:
        author = session.query(User).filter(User.author == author_name).one_or_none()
        if not author:
            author = User(author=author_name)
            session.add(author)
            session.commit()
        
        new_post = Post(title=title, content=content, author=author)
        session.add(new_post)
        session.commit()
        
        messagebox.showinfo("Success", f"Post '{title}' created successfully!")
        title_entry.delete(0, tk.END)
        content_text.delete("1.0", tk.END)
        author_entry.delete(0, tk.END)
        list_posts()
    else:
        messagebox.showwarning("Input Error", "Please provide all details.")


# Create a function that will allow the user to view, or READ, all the available blog posts
def list_posts():
    posts = session.query(Post).all()
    post_list_text.delete("1.0", tk.END)
    if posts:
        for post in posts:
            post_list_text.insert(
                tk.END, 
                f"ID: {post.id} | Title: {post.title} | Author: {post.author.author} | Published on: {post.publication_date}\n"
            )
    else:
        post_list_text.insert(tk.END, "No posts available.\n")

# Create a function that allows a user to UPDATE their blog post
def update_post():
    try:
        post_id = int(post_id_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid Post ID.")
        return
    
    new_title = title_entry.get()
    new_content = content_text.get("1.0", tk.END)
    
    post = session.query(Post).filter(Post.id == post_id).one_or_none()
    if post:
        if new_title:
            post.title = new_title
        if new_content.strip(): 
            post.content = new_content.strip()
        session.commit()
        messagebox.showinfo("Success", "Post updated successfully!")
        list_posts()
    else:
        messagebox.showerror("Not Found", "Post not found.")
    
    post_id_entry.delete(0, tk.END)

# Create a function that enables a user to DELETE a blog post
def delete_post():
    try:
        post_id = int(post_id_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid Post ID.")
        return
    
    post = session.query(Post).filter(Post.id == post_id).one_or_none()
    if post:
        session.delete(post)
        session.commit()
        messagebox.showinfo("Success", "Post deleted successfully!")
        list_posts()
    else:
        messagebox.showerror("Not Found", "Post not found.")
    
    post_id_entry.delete(0, tk.END)

# Updated function to view a post and clear the Post ID field
def view_post():
    try:
        post_id = int(post_id_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid Post ID.")
        return
    
    post = session.query(Post).filter(Post.id == post_id).one_or_none()
    if post:
        view_window = tk.Toplevel(root)
        view_window.title(f"Post ID {post.id} - {post.title}")
        view_window.geometry("400x300")
        
        tk.Label(view_window, text="Title:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        tk.Label(view_window, text=post.title).pack(anchor="w", padx=10, pady=5)

        tk.Label(view_window, text="Author:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        tk.Label(view_window, text=post.author.author).pack(anchor="w", padx=10, pady=5)

        tk.Label(view_window, text="Published on:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        tk.Label(view_window, text=post.publication_date).pack(anchor="w", padx=10, pady=5)

        tk.Label(view_window, text="Content:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        content_display = scrolledtext.ScrolledText(view_window, width=45, height=10, wrap="word")
        content_display.pack(anchor="w", padx=10, pady=5)
        content_display.insert(tk.END, post.content)
        content_display.config(state=tk.DISABLED)
    else:
        messagebox.showerror("Not Found", "Post not found.")
    
    post_id_entry.delete(0, tk.END)
    
def github():
    url = "https://www.github.com/spowers0409"
    webbrowser.open(url)

# Create a TKinter instance to create the gui window
root = tk.Tk()
root.title("Blog Post CRUD Operations")
root.geometry("600x550")

# Create a text box for a blog title
tk.Label(root, text="Title:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
title_entry = tk.Entry(root, width=40)
title_entry.grid(row=0, column=1, padx=10, pady=5)

# Create a text box for adding blog content
tk.Label(root, text="Content:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
content_text = scrolledtext.ScrolledText(root, width=40, height=5, wrap="word")
content_text.grid(row=1, column=1, padx=10, pady=5)
content_text.bind("<Tab>", focus_next_widget)

# Create a text box to include the author of the blog
tk.Label(root, text="Author:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
author_entry = tk.Entry(root, width=40)
author_entry.grid(row=2, column=1, padx=10, pady=5)

# Create a text box to enter the ID for Read, Update, and Delete functions
tk.Label(root, text="Post ID:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
post_id_entry = tk.Entry(root, width=20)
post_id_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

# Create the necessary buttons to be able to navigate blog posts
# Create a "Create Post" button
create_button = tk.Button(root, text="Create Post", command=create_post)
create_button.grid(row=4, column=0, padx=10, pady=10)

# Create a "List Posts" button
list_button = tk.Button(root, text="List Posts", command=list_posts)
list_button.grid(row=4, column=1, padx=10, pady=10, sticky="w")

# Create an "Update Posts" button
update_button = tk.Button(root, text="Update Post", command=update_post)
update_button.grid(row=5, column=0, padx=10, pady=10)

# Create a "Delete Post" button
delete_button = tk.Button(root, text="Delete Post", command=delete_post)
delete_button.grid(row=5, column=1, padx=10, pady=10, sticky="w")

# Create a "View Post" button
view_button = tk.Button(root, text="View Post", command=view_post)
view_button.grid(row=6, column=0, padx=10, pady=10)

# List all of the posts text box
post_list_text = scrolledtext.ScrolledText(root, width=70, height=10, wrap="word")
post_list_text.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
post_list_text.bind("<Tab>", focus_next_widget)

# Create a button to open the Github page for this project
gh_button = tk.Button(root, text = "View on Github", command=github)
gh_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)