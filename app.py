import streamlit as st
import json
import KnowledgeFeed.main as kf
from streamlit_carousel import carousel
import random


# Initialize interaction_metrics in session state
if "interaction_metrics" not in st.session_state:
    st.session_state.interaction_metrics = {}


# Function to generate random author names
def generate_random_name():
    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"]  # Add more names
    return random.choice(names)


# Placeholder for your API call function
def call_api(user_input, query_type, start):
    """
    Calls your external package/API to get the JSON response.
    Replace this with your actual API call.
    """
    # test data
    with open("test.json", "r") as f: data = json.load(f)
    # real data
    # data = kf.FeedBuilder().build_feed(user_input, query_type, start)
    return data

def incrementcount(interaction_metrics, post_key):
    interaction_metrics[post_key]["upvotes"] += 1


def display_post(post, obj_id):
    post_key = f"{obj_id}-{post['postID']}"
    interaction_metrics = st.session_state.interaction_metrics # Access from the session state


    if post_key not in interaction_metrics:
        interaction_metrics[post_key] = {"upvotes": 0, "downvotes": 0}

    
    with st.container(border=True, key=post_key):  # Add unique key to container
        # Author information
        src = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTTRADlISn22Ijhw70O9AR-pjZ7QUHTmHDaSw&s"
        author_name = generate_random_name() #Generate author name for each post
        st.markdown(f'<div style="display: flex; align-items: center;"><img src={src} width="50" height="50" style="border-radius: 50%; margin-right: 10px; margin-bottom: 10px;"><span>{author_name}</span></div>', unsafe_allow_html=True) #Display author info with image

        st.write(post["text"])

        media_items = []
        for resource in post.get("resources", []): #Handle missing resources
            for img in resource.get("images", []): #Handle missing images
                media_items.append({"text": "image text", "img": img["image"], "title": img.get("title", "")})  # Handle missing title
        if media_items:
            carousel(items=media_items, container_height=300, key=f"carousel_{obj_id}")

        col1, col2 = st.columns([1, 1])

        col1.button(f"Upvote", key=f"upvote-{post_key}", on_click=incrementcount(interaction_metrics, post_key))
            
            


        if col2.button(f"Downvote", key=f"downvote-{post_key}"):
            interaction_metrics[post_key]["downvotes"] += 1
            
 

        # Chat with Agent (WhatsApp-like)
        with st.expander(f"Chat with {author_name}"): #Use the same author name
            chat_key = f"chat-{post_key}"  # Unique chat key
            if chat_key not in st.session_state:
                st.session_state[chat_key] = []

            for message in st.session_state[chat_key]:
                st.markdown(
                    f'<div style="background-color: #e0e0e0; padding: 10px; margin-bottom: 5px; border-radius: 5px;">{message["user"]}: {message["text"]}</div>',
                    unsafe_allow_html=True,
                )

            new_message = st.text_area("Type your message...", key=f"new-message-{chat_key}")
            if st.button("Send", key=f"send-{chat_key}") and new_message:
                st.session_state[chat_key].append({"user": "You", "text": new_message})
                # Add agent's response (replace with your agent logic)
                st.session_state[chat_key].append({"user": author_name, "text": "Agent's response here..."}) #Agent response
                st.rerun()
 


        ddgs = {
            "model": "llama-3.3-70b",
            "source": "ddgs",
            "personality": "assistant",
            "temp": 0.7,
        }
        groq = {
            "model": "llama-3.3-70b-versatile",
            "source": "groq",
            "personality": "assistant",
            "temp": 0.7,
        }    

        if st.button(f"Change Character", key=f"config-{post_key}"):
            selected_option = st.selectbox("Select an option", ("Option 1", "Option 2", "Option 3", "Option 4"))
            if selected_option:
                st.write(f"Selected option: {selected_option}")


# ... (Main Streamlit app)
st.title("Knowledge Feed")

user_input = st.text_input("Enter your input:")
query_type = st.selectbox("What type of search would you like?",
                          ("academic", "business"))
start = 0

if st.button("Load Posts"):
    if user_input:
        with st.spinner("Loading posts..."):
            # prod delivery
            for item in kf.FeedBuilder().build_feed(user_input, query_type, start):  # Iterate directly
                # print(f"Item from stream: {item}")
            # testing delivery
            # data = call_api("hello", "hello", 0)
            
            # print(data)
            # for item in data:
                obj_id = item['objectID']
                for post in item["posts"]:
                    post_key = f"{obj_id}-{post['postID']}"

                    # print(f"Post from stream: {post}")
                    display_post(post, item["objectID"]) #Display each post as it comes.
                    print(f"rendered post {post_key}" )
    else:
        st.write("Please enter input")

# Display Interaction Metrics (for debugging/monitoring)
st.write("Interaction Metrics:", st.session_state.interaction_metrics)


# CSS for LinkedIn-style layout and responsiveness
st.markdown(
    """
    <style>
    .post-container {
        margin-bottom: 20px;
        padding: 15px;
        border: 1px solid #eee; /* Add a border if needed */
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stButton {
        margin-right: 10px; /* Space between buttons */
    }

    @media (max-width: 768px) {
        .post-container {
            width: 95%; /* Make posts almost full width on mobile */
            margin: 10px auto; /* Center on mobile */
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)