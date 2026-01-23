import streamlit as st
st.title("VAK Quiz")
st.write("Welcome to the VAK (Visual, Auditory, Kinesthetic) learning style quiz!")
st.write("This quiz will help you determine your preferred learning style.")
# Questions and options
questions = [
    {
        "question": "When you are trying to remember a phone number, you:",
        "options": [
            "Visualize the numbers in your mind.",
            "Repeat the numbers out loud.",
            "Write the numbers down or use your fingers to count."
        ]
    },
    {
        "question": "When learning a new skill, you prefer to:",
        "options": [
            "Watch a demonstration or video.",
            "Listen to instructions or explanations.",
            "Try it out yourself and learn by doing."
        ]
    },
    {
        "question": "In a classroom setting, you find it easiest to learn when:",
        "options": [
            "There are visual aids like charts and diagrams.",
            "The teacher explains concepts verbally.",
            "You can engage in hands-on activities."
        ]
    }
]

# Initialize scores
scores = {"Visual": 0, "Auditory": 0, "Kinesthetic": 0}
# Quiz logic
for q in questions:
    st.write(q["question"])
    choice = st.radio("", q["options"], key=q["question"])
    if choice == q["options"][0]:
        scores["Visual"] += 1
    elif choice == q["options"][1]:
        scores["Auditory"] += 1
    else:
        scores["Kinesthetic"] += 1 
st.write("---")
# Determine learning style  
max_score = max(scores.values())
learning_style = [k for k, v in scores.items() if v == max_score]
st.write(f"Your learning style is: {learning_style[0]}")    
st.write("Thank you for taking the VAK quiz! Explore more about your learning style and how to leverage it for effective learning.")
