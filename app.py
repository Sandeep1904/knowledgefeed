import streamlit as st
import json
import KnowledgeFeed.main as kf

from streamlit_carousel import carousel  # For image/video slider

# Initialize interaction_metrics in session state
if "interaction_metrics" not in st.session_state:
    st.session_state.interaction_metrics = {}

interaction_metrics = st.session_state.interaction_metrics # Access from the session state

# Placeholder for your API call function
def call_api(user_input, query_type, start):
    """
    Calls your external package/API to get the JSON response.
    Replace this with your actual API call.
    """
    # test data
    # with open("test.json", "r") as f: data = json.load(f)
    # real data
    data = kf.FeedBuilder().build_feed(user_input, query_type, start)
    return data


def display_post(post, obj_id):

    post_key = f"{obj_id}-{post['postID']}"  # Unique key

    if post_key not in interaction_metrics:
        interaction_metrics[post_key] = {"upvotes": 0, "downvotes": 0}  # Initialize

    with st.container(border=True): #Card like container for each post
        st.write(post["text"])

        media_items = []
        for resource in post.get("resources", []):
            for img in resource.get("images", []):
                media_items.append({"text": "image text", "img": img["image"], "title": img["title"]})
            # for vid in resource.get("videos", []):
            #     media_items.append({"type": "video", "content": vid["video"], "title": vid["title"]})
        if media_items:
            carousel(items=media_items, container_height=300)

        col1, col2 = st.columns([1, 1])  # Upvote/Downvote/Chat

        if col1.button(f"Upvote", key=f"upvote-{post_key}"):  # Unique keys for buttons
            interaction_metrics[post_key]["upvotes"] += 1
        if col2.button(f"Downvote", key=f"downvote-{post_key}"):
            interaction_metrics[post_key]["downvotes"] += 1

        # Comment Section (Expandable)
        with st.expander("Chat with Mark"):
            comment_key = f"comments-{post_key}"
            if comment_key not in st.session_state:
                st.session_state[comment_key] = []  # Initialize comments

            new_comment = st.text_area("Add a comment:", key=f"text-{comment_key}")
            if st.button("Submit", key=f"submit-{comment_key}") and new_comment:
                st.session_state[comment_key].append(new_comment)
                st.experimental_rerun()  # Refresh to show the new comment

            for comment in st.session_state[comment_key]:
                st.write(f"- {comment}")

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
            for item in kf.FeedBuilder().build_feed(user_input, query_type, start):  # Iterate directly
                for post in item["posts"]:
                    display_post(post, item["objectID"]) #Display each post as it comes.
                    print(f"rendered post {post['postID']}" )
    else:
        st.write("Please enter input")

# Display Interaction Metrics (for debugging/monitoring)
st.write("Interaction Metrics:", interaction_metrics)


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