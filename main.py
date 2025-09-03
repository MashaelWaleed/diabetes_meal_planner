from experta import *

class DiabetesExpert(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        print(Utils.prRed("\n🩸 Welcome to the Diabetes Meal Planning Expert System 🩸"))
        yield Fact(phase="initial")
        yield Fact(need="basic_info")
    # hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
    # Rule 1: Basic Information Collection
    @Rule(
        Fact(phase="initial"),
        Fact(need="basic_info"),
        NOT(Fact(personal_info_collected=True)))
    def collect_personal_info(self):
        print("\n📋I'm going to ask you about some of your personal information: ")
        gender = input(Utils.prGreen("> What is your gender? (female/male): ")).strip().lower()
        age = int(input(Utils.prGreen("> What is your age?: ")))
        weight = float(input(Utils.prGreen("> What is your weight in kilograms?: ")))
        height = float(input(Utils.prGreen("> What is your height in centimeters?: ")))
        pregnancy = input(Utils.prGreen("> Are you pregnant? (yes/no): ")).strip().lower() if gender == "female" else "no"
        
        self.declare(Fact(gender=gender))
        self.declare(Fact(age=age))
        self.declare(Fact(weight=weight))
        self.declare(Fact(height=height))
        self.declare(Fact(pregnant=(pregnancy == "yes")))
        self.declare(Fact(personal_info_collected=True))
        self.declare(Fact(need="medical_info"))


    # Rule 2: Medical Information Collection
    @Rule(Fact(need="medical_info"), NOT(Fact(medical_info_collected=True)))
    def collect_medical_info(self):
        print("\n🏥 Now I'm going to ask you about your health: ")
        diabetes_type = int(input(Utils.prGreen("> What type of diabetes do you have? (1/2): ")))
        current_hba1c = float(input(Utils.prGreen("> What is your current hba1c level? (%): ")))
        
        self.declare(Fact(diabetes_type=diabetes_type))
        self.declare(Fact(current_hba1c=current_hba1c))
        self.declare(Fact(medical_info_collected=True))
        self.declare(Fact(need="lifestyle_info"))

    # Rule 3: Lifestyle Information Collection
    @Rule(Fact(need="lifestyle_info"), NOT(Fact(lifestyle_info_collected=True)))
    def collect_lifestyle_info(self):
        print("\n🏃 Now I need some information about your lifestyle: ")
        activity_level = input(Utils.prGreen("> Activity level? (sedentary/light/moderate/active/very_active): ")).strip().lower()
        stress_level = input(Utils.prGreen("> Stress level? (low/moderate/high): ")).strip().lower()
        sleep_hours = float(input(Utils.prGreen("> Average hours of sleep per night?: ")))
        
        self.declare(Fact(activity_level=activity_level))
        self.declare(Fact(stress_level=stress_level))
        self.declare(Fact(sleep_hours=sleep_hours))
        self.declare(Fact(lifestyle_info_collected=True))
        self.declare(Fact(need="dietary_info"))

    # Rule 4: Dietary Information Collection
    @Rule(
        Fact(need="dietary_info"),
        NOT(Fact(dietary_info_collected=True))
    )
    def collect_dietary_info(self):
        print("\n🥗 Now I need to ask you about your diet: ")
        meal_frequency = int(input(Utils.prGreen("> Preferred number of meals per day (3-6): ")))
        snacks = int(input(Utils.prGreen("> Preferred number of snacks per day (0-3): ")))
        
        self.declare(Fact(meal_frequency=meal_frequency))
        self.declare(Fact(snacks=snacks))
        self.declare(Fact(dietary_info_collected=True))
        self.declare(Fact(need="risk_assessment"))

    # Rule 5: Risk Assessment
    @Rule(
        Fact(need="risk_assessment"),
        Fact(current_hba1c=MATCH.hba1c),
        Fact(age=MATCH.age),
        Fact(diabetes_type=MATCH.diabetes_type),
        NOT(Fact(risk_level=W()))
    )
    def assess_risk_level(self, hba1c, age, diabetes_type):
        risk_level = "low"
        
        if hba1c > 8.0 or (age > 65 and diabetes_type == 1) or (hba1c > 7.5 and diabetes_type == 2):
            risk_level = "high"
        elif hba1c > 7.0 or age > 60:
            risk_level = "moderate"
            
        self.declare(Fact(risk_level=risk_level))
        print(Utils.prYellow(f"\n⚠️ Risk Assessment: {risk_level.upper()} risk level detected") )
        self.declare(Fact(need="caloric_calculation"))

    # Rule 6: Caloric Calculation
    @Rule(
        Fact(need="caloric_calculation"),
        Fact(gender=MATCH.gender),
        Fact(age=MATCH.age),
        Fact(weight=MATCH.weight),
        Fact(height=MATCH.height),
        Fact(activity_level=MATCH.activity_level),
        Fact(pregnant=MATCH.pregnant),
        NOT(Fact(daily_calories=W()))
    )
    def calculate_calories(self, gender, age, weight, height, activity_level, pregnant):
        activity_factors = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        # Base BMR calculation
        if gender == "female":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            
        # Apply activity factor
        calories = bmr * activity_factors[activity_level]
        
        # Pregnancy adjustment
        if pregnant:
            calories += 300
            
        self.declare(Fact(daily_calories=calories))
        self.declare(Fact(need="macro_calculation"))

    # Rule 7: Macro Calculation
    @Rule(
        Fact(need="macro_calculation"),
        Fact(daily_calories=MATCH.calories),
        Fact(diabetes_type=MATCH.diabetes_type),
        Fact(activity_level=MATCH.activity_level),
        NOT(Fact(macros_calculated=True))
    )
    def calculate_macros(self, calories, diabetes_type, activity_level):
        if diabetes_type == 1:
            carb_percentage = 45 if activity_level in ["active", "very_active"] else 40
            protein_percentage = 20 if activity_level in ["sedentary", "light"] else 25
            fat_percentage = 100 - carb_percentage - protein_percentage
        else:  # Type 2
            carb_percentage = 40 if activity_level in ["active", "very_active"] else 35
            protein_percentage = 25 if activity_level in ["sedentary", "light"] else 30
            fat_percentage = 100 - carb_percentage - protein_percentage
            
        carb_grams = (calories * (carb_percentage/100)) / 4
        protein_grams = (calories * (protein_percentage/100)) / 4
        fat_grams = (calories * (fat_percentage/100)) / 9
        
        self.declare(Fact(carb_grams=carb_grams))
        self.declare(Fact(protein_grams=protein_grams))
        self.declare(Fact(fat_grams=fat_grams))
        self.declare(Fact(macros_calculated=True))
        self.declare(Fact(need="meal_distribution"))

    # Rule 8: Meal Distribution
    @Rule(
        Fact(need="meal_distribution"),
        Fact(meal_frequency=MATCH.meals),
        Fact(carb_grams=MATCH.carbs),
        Fact(protein_grams=MATCH.protein),
        Fact(fat_grams=MATCH.fat),
        NOT(Fact(meal_distribution_complete=True))
    )
    def plan_meal_distribution(self, meals, carbs, protein, fat):
        print("\n🍽️  Daily Meal Distribution:")
        
        meal_percentages = {
            3: [0.30, 0.35, 0.35],  # Breakfast (30%), Lunch (35%), Dinner (35%)
            4: [0.25, 0.30, 0.25, 0.20],  # Breakfast (25%), Lunch (30%), Dinner (25%), Light Dinner (20%)
            5: [0.20, 0.25, 0.25, 0.15, 0.15],  # Breakfast (20%), Lunch (25%), Dinner (25%), Light Dinner (15%), Pre-Bed Snack (15%)
            6: [0.20, 0.20, 0.20, 0.15, 0.15, 0.10]  # Mid-Morning Snack (20%), Breakfast (20%), Lunch (20%), Dinner (15%), Light Dinner (15%), Evening Snack (10%)
        }

        chosen_distribution = meal_percentages[meals]
        
        for i, percentage in enumerate(chosen_distribution, 1):
            meal_carbs = carbs * percentage
            meal_protein = protein * percentage
            meal_fat = fat * percentage
            print(Utils.prLightPurple(f"\nMeal {i}:"))
            print(Utils.prLightPurple(f"- Carbohydrates: {meal_carbs:.1f}g"))
            print(Utils.prLightPurple(f"- Protein: {meal_protein:.1f}g"))
            print(Utils.prLightPurple(f"- Fat: {meal_fat:.1f}g"))
            
        self.declare(Fact(meal_distribution_complete=True))
        self.declare(Fact(need="recommendations"))

    # Rule 9: Recommendations
    @Rule(
        Fact(need="recommendations"),
        Fact(risk_level=MATCH.risk),
        Fact(stress_level=MATCH.stress),
        Fact(sleep_hours=MATCH.sleep),
        NOT(Fact(recommendations_provided=True))
    )
    def provide_recommendations(self, risk, stress, sleep):
        print("\n📋 I Recommend:")
        
        # Risk-based recommendations
        if risk == "high":
            print(Utils.prYellow("- Monitor blood glucose more frequently (at least 4 times daily)"))
            print(Utils.prYellow("- Consider using a continuous glucose monitor"))
            print(Utils.prYellow("- Schedule regular check-ups with your healthcare provider"))

        # Stress management recommendations
        if stress == "high":
            print(Utils.prYellow("- Consider stress-reduction techniques like meditation or yoga"))
            print(Utils.prYellow("- Monitor blood sugar more frequently during high-stress periods"))

        # Sleep recommendations
        if sleep < 7:
            print(Utils.prYellow("- Aim to increase sleep duration to 7-8 hours per night"))
            print(Utils.prYellow("- Consider establishing a regular sleep schedule"))

        print("\n⚠️ Important Reminders:")
        print(Utils.prYellow("- Always take medications as prescribed"))
        print(Utils.prYellow("- Keep a food and blood glucose diary"))
        print(Utils.prYellow("- Stay hydrated throughout the day"))
        print(Utils.prYellow("- Adjust meal plans based on blood glucose readings"))
    
        self.declare(Fact(recommendations_provided=True))
    

class Utils:
    @staticmethod
    def prRed(skk): 
        return "\033[91m{}\033[00m".format(skk)
    
    @staticmethod
    def prGreen(skk): 
        return "\033[92m{}\033[00m".format(skk)
    
    @staticmethod
    def prYellow(skk): 
        return "\033[93m{}\033[00m".format(skk)
    
    @staticmethod
    def prLightPurple(skk): 
        return "\033[94m{}\033[00m".format(skk)
    

if __name__ == "__main__":
    engine = DiabetesExpert()
    engine.reset()  # Prepare the engine for a new session
    engine.run()  # Run the engine to trigger rules
    print(Utils.prRed("\n\n🩸 Thank you for using the Diabetes Meal Planning Expert System 🩸\n"))
