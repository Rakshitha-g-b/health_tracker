from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import MoodEntry, HealthSymptom, DailyHabit
from .forms import MoodEntryForm, HealthSymptomForm, DailyHabitForm
from datetime import datetime, timedelta
import re

def get_mood_suggestions(sentiment, mood_level, text):
    # Define mood level ranges and their specific suggestions
    mood_ranges = {
        'very_sad': {  # 1
            'suggestions': [
                "It's okay to feel this way. Remember that tough times don't last forever.",
                "You're not alone in this. Consider reaching out to someone you trust.",
                "Small steps matter. Try doing one small thing that brings you comfort.",
                "Practice self-compassion. Be kind to yourself like you would to a friend.",
                "This feeling is temporary. Tomorrow is a new day with new possibilities."
            ],
            'encouragement': [
                "You're stronger than you think. Every step forward, no matter how small, is progress.",
                "Your feelings are valid, and it's okay to ask for help when needed.",
                "Remember that even the darkest night will end and the sun will rise.",
                "You've overcome challenges before, and you can do it again.",
                "Take it one moment at a time. You don't have to figure everything out right now."
            ]
        },
        'sad': {  # 2
            'suggestions': [
                "Try to focus on small positive moments in your day.",
                "Engage in activities that usually bring you comfort or joy.",
                "Connect with nature - even a short walk can help shift your perspective.",
                "Practice gratitude by noting three things you're thankful for.",
                "Listen to uplifting music or watch something that makes you smile."
            ],
            'encouragement': [
                "You're doing better than you think. Keep going!",
                "Every day is a new opportunity for positive change.",
                "Your resilience is growing with each challenge you face.",
                "Small improvements add up to big changes over time.",
                "You have the strength to turn things around."
            ]
        },
        'neutral': {  # 3
            'suggestions': [
                "This is a good time to build positive habits.",
                "Try something new to add more joy to your day.",
                "Connect with friends or family to boost your mood.",
                "Set small, achievable goals to build momentum.",
                "Practice mindfulness to stay present and aware."
            ],
            'encouragement': [
                "Stability is a great foundation for growth!",
                "You're in a good place to make positive changes.",
                "Use this balanced state to build momentum.",
                "Every day is an opportunity to move forward.",
                "You're building a strong foundation for happiness."
            ]
        },
        'happy': {  # 4
            'suggestions': [
                "Share your positive energy with others.",
                "Document what's contributing to your good mood.",
                "Plan activities that maintain this positive state.",
                "Express gratitude to people in your life.",
                "Use this energy for creative or productive projects."
            ],
            'encouragement': [
                "Wonderful! Keep nurturing these positive feelings!",
                "Your positive energy is contagious - spread it around!",
                "This is a great time to build lasting positive habits.",
                "Your happiness is well-deserved - enjoy it!",
                "Use this momentum to create more joy in your life."
            ]
        },
        'very_happy': {  # 5
            'suggestions': [
                "Share your joy with others - it's contagious!",
                "Document what's working well in your life.",
                "Plan ways to maintain this positive momentum.",
                "Express gratitude and appreciation to others.",
                "Use this energy to help or inspire someone else."
            ],
            'encouragement': [
                "Amazing! Your positive energy is shining through!",
                "This is wonderful - keep spreading the joy!",
                "Your happiness is inspiring - share it with others!",
                "You're creating a positive ripple effect around you.",
                "This is a great time to build lasting happiness habits."
            ]
        }
    }

    # Get mood range based on mood level
    if mood_level == 1:
        mood_range = 'very_sad'
    elif mood_level == 2:
        mood_range = 'sad'
    elif mood_level == 3:
        mood_range = 'neutral'
    elif mood_level == 4:
        mood_range = 'happy'
    else:  # 5
        mood_range = 'very_happy'

    # Get base suggestions and encouragement from mood range
    suggestions = mood_ranges[mood_range]['suggestions']
    encouragement = mood_ranges[mood_range]['encouragement']

    # Create analysis text
    analysis_text = [
        f"Mood Level: {mood_level}/5",
        f"Current Mood Range: {mood_range.replace('_', ' ').title()}",
        f"Sentiment Analysis: {sentiment}",
        "\nPersonalized Suggestions:"
    ]

    # Add mood-specific message
    if mood_level == 1:
        analysis_text.append("\nI notice you're feeling very sad. Remember that it's okay to feel this way, and you're not alone.")
    elif mood_level == 2:
        analysis_text.append("\nI see you're feeling sad. Let's work on lifting your spirits:")
    elif mood_level == 3:
        analysis_text.append("\nYou're in a neutral state. Here are some ways to build on this:")
    elif mood_level == 4:
        analysis_text.append("\nGreat! You're feeling happy. Here's how to maintain this energy:")
    else:
        analysis_text.append("\nWonderful! You're feeling very happy. Here's how to keep this momentum going:")

    # Add suggestions
    analysis_text.extend([f"- {s}" for s in suggestions])

    # Add encouragement
    analysis_text.append("\nWords of Encouragement:")
    analysis_text.extend([f"- {e}" for e in encouragement])

    if mood_level <= 2:
        analysis_text.append("\nRemember: If you continue to feel low, don't hesitate to seek professional support. You deserve to feel better.")

    return "\n".join(analysis_text)

def simple_sentiment_analysis(text):
    positive_words = {
        'happy': 0.8, 'good': 0.6, 'great': 0.8, 'awesome': 0.9, 'excellent': 0.9,
        'joy': 0.8, 'wonderful': 0.9, 'fantastic': 0.9, 'amazing': 0.9,
        'delighted': 0.8, 'pleased': 0.7, 'content': 0.6, 'satisfied': 0.7,
        'grateful': 0.7, 'blessed': 0.8, 'thrilled': 0.9, 'ecstatic': 1.0,
        'overjoyed': 1.0, 'cheerful': 0.7, 'upbeat': 0.7, 'positive': 0.6,
        'optimistic': 0.7, 'peaceful': 0.6, 'calm': 0.5, 'relaxed': 0.5
    }
    
    negative_words = {
        'sad': -0.7, 'bad': -0.6, 'terrible': -0.9, 'awful': -0.9, 'horrible': -0.9,
        'unhappy': -0.7, 'depressed': -0.9, 'angry': -0.8, 'frustrated': -0.6,
        'annoyed': -0.5, 'upset': -0.6, 'disappointed': -0.6, 'worried': -0.6,
        'anxious': -0.7, 'stressed': -0.7, 'tired': -0.5, 'exhausted': -0.7,
        'drained': -0.6, 'overwhelmed': -0.7, 'negative': -0.6, 'pessimistic': -0.7,
        'miserable': -0.9, 'lonely': -0.7, 'hopeless': -0.9, 'fear': -0.7
    }
    
    words = re.findall(r'\w+', text.lower())
    if not words:
        return "NEUTRAL", 0.5, []
    
    total_score = 0
    word_count = 0
    
    for word in words:
        if word in positive_words:
            total_score += positive_words[word]
            word_count += 1
        elif word in negative_words:
            total_score += negative_words[word]
            word_count += 1
    
    if word_count == 0:
        polarity = 0
    else:
        polarity = total_score / len(words)  # Normalize by total words for better context
    
    # Determine sentiment based on polarity
    if polarity > 0.1:
        sentiment = "POSITIVE"
    elif polarity < -0.1:
        sentiment = "NEGATIVE"
    else:
        sentiment = "NEUTRAL"
    
    return sentiment, abs(polarity), polarity

@login_required
def dashboard(request):
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # Get recent entries
    recent_moods = MoodEntry.objects.filter(user=request.user, date__gte=week_ago).order_by('-date')
    recent_symptoms = HealthSymptom.objects.filter(user=request.user, date__gte=week_ago).order_by('-date')
    recent_habits = DailyHabit.objects.filter(user=request.user, date__gte=week_ago).order_by('-date')
    
    context = {
        'recent_moods': recent_moods,
        'recent_symptoms': recent_symptoms,
        'recent_habits': recent_habits,
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_mood(request):
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood_entry = form.save(commit=False)
            mood_entry.user = request.user
            
            # Get sentiment analysis
            sentiment, confidence, polarity = simple_sentiment_analysis(mood_entry.notes)
            
            # Get mood suggestions
            ai_analysis = get_mood_suggestions(sentiment, mood_entry.mood_level, mood_entry.notes)
            
            # Store the analysis
            mood_entry.ai_analysis = ai_analysis
            mood_entry.save()
            
            # Pass the analysis to the template
            return render(request, 'tracker/add_mood.html', {
                'form': MoodEntryForm(),  # Fresh form for new entry
                'ai_analysis': ai_analysis,
                'show_analysis': True,
                'success_message': 'Mood entry added successfully!'
            })
    else:
        form = MoodEntryForm()
    
    return render(request, 'tracker/add_mood.html', {
        'form': form,
        'show_analysis': False
    })

def get_symptom_suggestions(symptom_name, severity, notes):
    # AI Analysis of Notes
    note_keywords = {
        'throbbing': ['migraine', 'tension headache', 'cluster headache'],
        'dull': ['tension headache', 'sinus pressure', 'stress-related'],
        'sharp': ['nerve pain', 'acute condition', 'injury'],
        'chronic': ['long-term management', 'lifestyle changes', 'preventive care'],
        'acute': ['immediate relief', 'short-term treatment', 'emergency care'],
        'stress': ['relaxation techniques', 'stress management', 'mindfulness'],
        'anxiety': ['calming techniques', 'breathing exercises', 'mental health support'],
        'fatigue': ['energy management', 'sleep hygiene', 'nutritional support'],
        'pain': ['pain management', 'physical therapy', 'medication review'],
        'sleep': ['sleep hygiene', 'circadian rhythm', 'rest quality'],
        'diet': ['nutritional assessment', 'meal planning', 'dietary changes'],
        'exercise': ['physical activity', 'movement therapy', 'fitness routine'],
        'mood': ['emotional well-being', 'mental health', 'stress reduction'],
        'focus': ['cognitive function', 'attention management', 'brain health'],
        'energy': ['vitality', 'metabolic health', 'activity levels']
    }
    
    # Analyze notes for keywords
    note_analysis = []
    for keyword, suggestions in note_keywords.items():
        if keyword.lower() in notes.lower():
            note_analysis.extend(suggestions)
    
    # Get specific symptom suggestions
    symptom_keywords = {
        'headache': {
            'suggestions': [
                "Drink plenty of water (at least 8 glasses per day)",
                "Take a break from screens and rest your eyes",
                "Try a cold compress on your forehead",
                "Consider over-the-counter pain relief (ibuprofen or acetaminophen)",
                "Practice relaxation techniques like deep breathing",
                "Get some fresh air and take a short walk",
                "Massage your temples gently",
                "Try drinking ginger tea or peppermint tea"
            ],
            'severe': [
                "Consider consulting a healthcare provider if pain persists",
                "Monitor for any additional symptoms like nausea or vision changes",
                "Rest in a quiet, dark room",
                "Keep a headache diary to track triggers",
                "Consider professional massage therapy"
            ],
            'prevention': [
                "Maintain regular sleep schedule",
                "Stay hydrated throughout the day",
                "Take regular breaks from screens",
                "Practice stress management techniques",
                "Consider keeping a food diary to identify triggers"
            ]
        },
        'fatigue': {
            'suggestions': [
                "Ensure adequate sleep (7-9 hours per night)",
                "Stay hydrated with water and electrolyte drinks",
                "Take short breaks throughout the day",
                "Consider light exercise like walking or yoga",
                "Check your diet and ensure balanced nutrition",
                "Try power naps (20-30 minutes)",
                "Practice good sleep hygiene",
                "Consider vitamin D and B12 supplements"
            ],
            'severe': [
                "Consider a medical check-up for underlying conditions",
                "Review your sleep patterns with a specialist",
                "Check for potential nutritional deficiencies",
                "Monitor for symptoms of depression or anxiety",
                "Consider thyroid function tests"
            ],
            'prevention': [
                "Maintain consistent sleep schedule",
                "Exercise regularly",
                "Eat balanced meals at regular intervals",
                "Limit caffeine and sugar intake",
                "Practice stress reduction techniques"
            ]
        },
        'anxiety': {
            'suggestions': [
                "Practice deep breathing exercises (4-7-8 technique)",
                "Try mindfulness meditation for 10 minutes",
                "Take a short walk in nature",
                "Write down your thoughts and concerns",
                "Listen to calming music or nature sounds",
                "Try progressive muscle relaxation",
                "Drink chamomile or lavender tea",
                "Practice grounding techniques (5-4-3-2-1 method)"
            ],
            'severe': [
                "Consider professional support from a therapist",
                "Practice grounding techniques regularly",
                "Create a safe, quiet space for relaxation",
                "Consider cognitive behavioral therapy",
                "Keep a mood and anxiety diary"
            ],
            'prevention': [
                "Regular exercise and physical activity",
                "Maintain a consistent sleep schedule",
                "Practice daily mindfulness",
                "Limit caffeine and alcohol intake",
                "Build a strong support network"
            ]
        },
        'pain': {
            'suggestions': [
                "Apply heat or cold as appropriate for the type of pain",
                "Try gentle stretching exercises",
                "Take regular breaks from activities",
                "Consider over-the-counter pain relief",
                "Practice relaxation techniques",
                "Try massage or self-massage",
                "Use proper posture and ergonomics",
                "Consider physical therapy exercises"
            ],
            'severe': [
                "Seek medical attention if pain persists",
                "Monitor for any changes in pain patterns",
                "Keep a pain diary to track triggers",
                "Consider professional physical therapy",
                "Discuss pain management options with a doctor"
            ],
            'prevention': [
                "Maintain good posture",
                "Exercise regularly to strengthen muscles",
                "Use proper lifting techniques",
                "Take regular breaks from repetitive activities",
                "Stay active and maintain healthy weight"
            ]
        }
    }
    
    # Get general suggestions
    suggestions = []
    prevention_tips = []
    
    # Check for specific symptom matches
    symptom_lower = symptom_name.lower()
    for key, value in symptom_keywords.items():
        if key in symptom_lower:
            suggestions.extend(value['suggestions'])
            prevention_tips.extend(value['prevention'])
            if severity >= 7:  # Add severe suggestions for high severity
                suggestions.extend(value['severe'])
            break
    
    # If no specific suggestions found, add general ones
    if not suggestions:
        general_suggestions = [
            "Stay hydrated throughout the day",
            "Get adequate rest and sleep",
            "Monitor your symptoms closely",
            "Consider keeping a symptom diary",
            "Practice stress management techniques",
            "Maintain a balanced diet",
            "Exercise regularly",
            "Take regular breaks from activities"
        ]
        suggestions.extend(general_suggestions)
        if severity >= 7:
            suggestions.extend([
                "Consider consulting a healthcare provider",
                "Monitor for any changes in symptoms",
                "Keep track of symptom patterns",
                "Seek professional medical advice"
            ])
    
    # Create analysis text
    analysis_text = [
        f"Symptom: {symptom_name}",
        f"Severity: {severity}/10",
        "\nImmediate Actions:"
    ]
    analysis_text.extend([f"- {s}" for s in suggestions[:5]])
    
    if prevention_tips:
        analysis_text.extend([
            "\nPrevention Tips:"
        ])
        analysis_text.extend([f"- {p}" for p in prevention_tips[:3]])
    
    if note_analysis:
        analysis_text.extend([
            "\nAI Analysis of Your Notes:"
        ])
        analysis_text.extend([f"- Potential condition: {condition}" for condition in note_analysis[:3]])
        analysis_text.extend([
            "\nBased on your description, you might want to:"
        ])
        analysis_text.extend([f"- {s}" for s in suggestions[5:8]])
    
    if severity >= 7:
        analysis_text.extend([
            "\nNote: Your symptom severity is high. Please consider consulting a healthcare provider."
        ])
    
    return "\n".join(analysis_text)

@login_required
def add_symptom(request):
    if request.method == 'POST':
        form = HealthSymptomForm(request.POST)
        if form.is_valid():
            symptom = form.save(commit=False)
            symptom.user = request.user
            
            # Get AI analysis for the symptom
            ai_analysis = get_symptom_suggestions(
                symptom_name=form.cleaned_data['name'],
                severity=form.cleaned_data['severity'],
                notes=form.cleaned_data['notes']
            )
            
            # Store the AI analysis in the symptom
            symptom.ai_analysis = ai_analysis
            symptom.save()
            
            # Pass the analysis to the template
            return render(request, 'tracker/add_symptom.html', {
                'form': HealthSymptomForm(),  # Fresh form for new entry
                'ai_analysis': ai_analysis,
                'show_analysis': True,
                'success_message': 'Symptom added successfully!'
            })
    else:
        form = HealthSymptomForm()
    
    return render(request, 'tracker/add_symptom.html', {
        'form': form,
        'show_analysis': False
    })

def get_habit_analysis(sleep_hours, water_intake_ml, exercise_minutes, notes):
    analysis = []
    tips = []
    
    # Sleep analysis
    if sleep_hours < 7:
        analysis.append("Your sleep duration is below the recommended 7-9 hours.")
        tips.append("Try to establish a consistent sleep schedule and create a relaxing bedtime routine.")
    elif sleep_hours > 9:
        analysis.append("You're getting more sleep than typically recommended.")
        tips.append("While adequate sleep is important, excessive sleep might indicate underlying health issues.")
    else:
        analysis.append("Great job maintaining healthy sleep duration!")
        tips.append("Keep up the good sleep habits!")
    
    # Water intake analysis (convert ml to liters for analysis)
    water_liters = water_intake_ml / 1000
    if water_liters < 2:
        analysis.append(f"Your water intake ({water_intake_ml}ml) is below the recommended 2000-3000ml per day.")
        tips.append("Try carrying a water bottle with you and set reminders to drink water throughout the day.")
    elif water_liters > 4:
        analysis.append(f"Your water intake ({water_intake_ml}ml) is above typical recommendations.")
        tips.append("While staying hydrated is important, excessive water intake can be harmful. Consult a doctor if this is intentional.")
    else:
        analysis.append(f"Excellent hydration habits! You drank {water_intake_ml}ml of water.")
        tips.append("Maintain this healthy water intake level.")
    
    # Exercise analysis
    if exercise_minutes < 30:
        analysis.append("Your exercise duration is below the recommended 30 minutes per day.")
        tips.append("Try to incorporate more physical activity into your daily routine, even short walks can help.")
    elif exercise_minutes > 120:
        analysis.append("You're getting a lot of exercise!")
        tips.append("Make sure to include rest days and listen to your body's signals.")
    else:
        analysis.append("Good job maintaining regular exercise!")
        tips.append("Keep up the consistent physical activity!")
    
    # Create formatted analysis text
    analysis_text = [
        "Daily Habits Analysis:",
        "\n".join(analysis),
        "\nHealth Tips:",
        "\n".join([f"- {tip}" for tip in tips])
    ]
    
    return "\n".join(analysis_text)

@login_required
def add_habit(request):
    if request.method == 'POST':
        form = DailyHabitForm(request.POST)
        if form.is_valid():
            habit_entry = form.save(commit=False)
            habit_entry.user = request.user
            
            # Get habit analysis
            ai_analysis = get_habit_analysis(
                habit_entry.sleep_hours,
                habit_entry.water_intake_ml,
                habit_entry.exercise_minutes,
                habit_entry.notes
            )
            
            # Store the analysis
            habit_entry.ai_analysis = ai_analysis
            habit_entry.save()
            
            # Pass the analysis to the template
            return render(request, 'tracker/add_habit.html', {
                'form': DailyHabitForm(),  # Fresh form for new entry
                'ai_analysis': ai_analysis,
                'show_analysis': True,
                'success_message': 'Daily habit entry added successfully!'
            })
    else:
        form = DailyHabitForm()
    
    return render(request, 'tracker/add_habit.html', {
        'form': form,
        'show_analysis': False
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def delete_mood(request, mood_id):
    mood = get_object_or_404(MoodEntry, id=mood_id, user=request.user)
    if request.method == 'POST':
        mood.delete()
        messages.success(request, 'Mood entry deleted successfully.')
        return redirect('dashboard')
    return render(request, 'tracker/confirm_delete.html', {
        'object': mood,
        'type': 'mood entry'
    })

@login_required
def delete_symptom(request, symptom_id):
    symptom = get_object_or_404(HealthSymptom, id=symptom_id, user=request.user)
    if request.method == 'POST':
        symptom.delete()
        messages.success(request, 'Symptom entry deleted successfully.')
        return redirect('dashboard')
    return render(request, 'tracker/confirm_delete.html', {
        'object': symptom,
        'type': 'symptom entry'
    })

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(DailyHabit, id=habit_id, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit entry deleted successfully.')
        return redirect('dashboard')
    return render(request, 'tracker/confirm_delete.html', {
        'object': habit,
        'type': 'habit entry'
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})
