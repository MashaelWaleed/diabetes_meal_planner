from experta import *
import json


class DiabetesExpert(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        print(Utils.prRed("\n\nWelcome to the Diabetes Expert System 🩸\n"))
        print("Please answer the following questions to suggest a dietary for you\n")
        yield Fact(action="collect_data")  # Initial fact to start the process

        with open("meal_options.json") as f:
            self.meal_options = json.load(f)
        

    # Rule 1: If the user has not provided their gender, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(gender=W())), salience=1000)
    def ask_gender(self):
        gender = input(Utils.prGreen("\n> What is your gender? Female/Male:  "))  # Ask for the user's gender
        self.declare(Fact(gender=gender.strip().lower()))  # Store the gender as a fact

    # Rule 2: If the user has not provided their age, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(age=W())), salience=900)
    def ask_age(self):
        age = input(Utils.prGreen("\n> What is your age?  "))  # Ask for the user's age
        self.declare(Fact(age=int(age)))  # Store age as a fact

    # Rule 3: If the user has not provided their weight, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(weight=W())), salience=800)
    def ask_weight(self):
        weight = input(Utils.prGreen("\n> What is your weight in kilograms?  "))
        self.declare(Fact(weight=float(weight)))  # Store weight as a fact

    # Rule 4: If the user has not provided their height, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(height=W())), salience=700)
    def ask_height(self):
        height = input(Utils.prGreen("\n> What is your height in centimeters?  "))
        self.declare(Fact(height=float(height)))  # Store height as a fact
    
    # Rule 5: If the user has not provided their diabetes type, ask for it
    @Rule(Fact(action="collect_data"),  NOT(Fact(diabetes_type=W())), salience=600)
    def ask_diabetes_type(self):
        diabetes_type = input(Utils.prGreen("\n> What type of diabetes do you have? (1,2)  "))
        self.declare(Fact(diabetes_type=int(diabetes_type)))  # Store diabetes type as a fact

    # Rule 6: If the user has not provided their activity level, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(activity_level=W())), salience=400)
    def ask_activity_level(self):
        activity_level = input(Utils.prGreen("\n> What is your activity level? (sedentary, light, moderate, active, very active):  "))
        self.declare(Fact(activity_level=activity_level.strip().lower()))  # Store activity level as a fact

    # Rule 7: If the user has not provided their glucose level, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(glucose_level=W())), salience=300)
    def ask_glucose_level(self):
        glucose_level = input(Utils.prGreen("\n> What is your glucose level?  "))
        self.declare(Fact(glucose_level=float(glucose_level)))
        action_id = next(factId for factId, fact in self.facts.items() if fact.get('action'))
        if action_id:
            self.retract(action_id)
        self.declare(Fact(action="suggest_plan")) # update the action fact

    # Suggestions ------------------------------------------------------------------
    # Rule 8: check glucose level and warn user if it is too high or too low
    @Rule(Fact(action= "suggest_plan"), Fact(glucose_level=MATCH.glucose_level) , salience=250)
    def check_glucose_emergency(self, glucose_level):
        if glucose_level < 50:
            print(Utils.prRed("\n⚠️ EMERGENCY: Severely low blood sugar! Seek immediate medical attention!"))
        elif glucose_level > 300:
            print(Utils.prRed("\n⚠️ EMERGENCY: Severely high blood sugar! Seek immediate medical attention!"))

    # Rule 9: Calculate BMI once all data is collected and warn user if it indicates obesity
    @Rule(Fact(action= "suggest_plan"), Fact(weight=MATCH.weight), Fact(height=MATCH.height), salience=200)
    def calculate_bmi(self, weight, height):
        bmi = weight / ((height/100) ** 2)
        self.declare(Fact(bmi=bmi))
        if bmi > 30:
            print(Utils.prRed("\n⚠️ Warning: BMI indicates obesity. Consider consulting with a healthcare provider."))

     # Rule 10: Calculate BMR once all data is collected 
    @Rule(Fact(action="suggest_plan"), Fact(gender=MATCH.gender), Fact(age=MATCH.age), Fact(weight=MATCH.weight), Fact(height=MATCH.height), Fact(activity_level=MATCH.activity_level), salience=150)
    def calculate_bmr(self, gender, age, weight, height, activity_level):
        bmr = 0
        if gender == 'female':
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5

            # Calculate the activity factor based on the activity level
        activity_factor = 0
        if(activity_level == "sedentary"):
            activity_factor = 1.2
        elif(activity_level == "light"):
            activity_factor = 1.375
        elif(activity_level == "moderate"):
            activity_factor = 1.55
        elif(activity_level == "active"):
            activity_factor = 1.725
        elif(activity_level == "very active"):
            activity_factor = 1.9
        updatedBMR = activity_factor * bmr
        self.declare(Fact(bmr=updatedBMR))  # Store BMR as a fact

    # Rule 11: show recommendations based on diabetes type
    @Rule(Fact(action="suggest_plan"), Fact(diabetes_type=MATCH.diabetes_type), salience=100)
    def suggest_diabetes_type(self, diabetes_type):
        if diabetes_type == 1:
            print(Utils.prLightPurple("\nFor Type 1 diabetes: Balance carbs and protein, include post-exercise snacks to prevent hypoglycemia."))
        else:
            print(Utils.prLightPurple("\nFor Type 2 diabetes: Limit high-glycemic carbs, increase fiber intake with meals like vegetables, whole grains, and lean proteins."))

    # Rule 12: show recommendations based on glucose level
    @Rule(Fact(action="suggest_plan"), Fact(glucose_level=MATCH.glucose_level), salience=50)
    def suggest_glucose_level(self, glucose_level):
        if glucose_level < 70:
            print(Utils.prLightPurple("\nYour glucose level is low. Please consume 15-20 grams of glucose or simple carbs."))
        elif glucose_level >= 70 and glucose_level < 180:
            print(Utils.prLightPurple("\nYour glucose level is normal."))
        else:
            print(Utils.prLightPurple(("\nYour glucose level is high. Please drink water and avoid high-carb foods.")))


    # Rule 13: Adjust meal plan based on user data
    @Rule(Fact(action="suggest_plan"), Fact(bmr=MATCH.bmr), Fact(glucose_level=MATCH.glucose_level), salience=1)
    def adjust_meals(self, bmr, glucose_level):
        print(Utils.prLightPurple("\nBased on your data, we recommend the following meal plan:"))
        adjustedMeals = {}
        meals = {}
        if bmr < 1500:
            print("\nWe recommend a low-calorie meal plan")
            meals =self.meal_options['low_calorie']
        elif bmr >= 1500 and bmr < 2000:
            print("\nWe recommend a medium-calorie meal plan")
            meals =self.meal_options['medium_calorie']
        else:
            print("\nWe recommend a high-calorie meal plan")
            meals =self.meal_options['high_calorie']
        print(glucose_level)
        for mealTime, mealOptions in meals.items():
            adjustedMeals[mealTime] = []
            for meal in mealOptions:
                modifiedMeal = meal.copy()
                if glucose_level > 180:
                    if modifiedMeal['carbs'] > 30:
                        modifiedMeal['carbs'] = round(modifiedMeal['carbs'] * 0.8)  # Reduce carbs by 20%
                        modifiedMeal['details'] += " (reduced portion of carbs)"
                        modifiedMeal['calories'] = round(modifiedMeal['calories'] * 0.9)
                adjustedMeals[mealTime].append(modifiedMeal)

        self.print_meal_plan(adjustedMeals)

    #helper function to print meal plan
    def print_meal_plan(self, meal_plan):
        for meal_type, items in meal_plan.items():
            print(f"\n{meal_type.capitalize()}:")
            print(Utils.prYellow("-" * 30))
            for item in items:
                print(Utils.prYellow(f"Name: {item['name']}"))
                print(Utils.prYellow(f"  Calories: {item['calories']} kcal"))
                print(Utils.prYellow(f"  Details: {item['details']}"))
                print(Utils.prYellow(f"  Carbs: {item['carbs']} g"))
                print(Utils.prYellow(f"  Protein: {item['protein']} g"))
                print(Utils.prYellow(f"  Fats: {item['fats']} g"))
                print(Utils.prYellow(f"  Glucose Impact: {item['glucose_impact']}"))
                print(Utils.prYellow("-" * 30))
    

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
    print(Utils.prRed("\n\nThank you for using the Diabetes Expert System 🩸\n"))
