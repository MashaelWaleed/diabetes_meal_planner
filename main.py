from experta import *

class DiabetesExpert(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        print("Welcome to the Diabetes Expert System")
        print("Please answer the following questions to help us diagnose your condition")
        yield Fact(action="collect_data")  # Initial fact to start the process

    # Rule 1: If the user has not provided their gender, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(gender=W())), salience=1000)
    def ask_gender(self):
        gender = input("What is your gender? Female/Male: ")  # Ask for the user's gender
        self.declare(Fact(gender=gender.strip().lower()))  # Store the gender as a fact

    # Rule 2: If the user has not provided their age, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(age=W())), salience=900)
    def ask_age(self):
        age = input("What is your age? ") 
        self.declare(Fact(age=int(age)))  # Store age as a fact

    # Rule 3: If the user has not provided their weight, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(weight=W())), salience=800)
    def ask_weight(self):
        weight = input("What is your weight in kilograms? ")
        self.declare(Fact(weight=float(weight)))  # Store weight as a fact

    # Rule 4: If the user has not provided their height, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(height=W())), salience=700)
    def ask_height(self):
        height = input("What is your height in centimeters? ")
        self.declare(Fact(height=float(height)))  # Store height as a fact

    # Rule 5: Calculate BMR once all data is collected
    @Rule(Fact(action="collect_data"), Fact(gender=MATCH.gender), Fact(age=MATCH.age), Fact(weight=MATCH.weight), Fact(height=MATCH.height), salience=600)
    def calculate_bmr(self, gender, age, weight, height):
        bmr = 0
        if gender == 'female':
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        self.declare(Fact(bmr=bmr))  # Store BMR as a fact
        print(f"Your BMR is: {bmr}")

    # Rule 6: If the user has not provided their activity level, ask for it
    @Rule(Fact(action="collect_data"), Fact(bmr = MATCH.bmr) , NOT(Fact(activity_level=W())), salience=500)
    def ask_activity_level(self, bmr):
        activity_level = input("What is your activity level? (sedentary, light, moderate, active, very active): ")
        self.declare(Fact(activity_level=activity_level.strip().lower()))  # Store activity level as a fact
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
        print(self.facts.items())
        updatedBMR = activity_factor * bmr
        bmr_id = next(factId for factId, fact in self.facts.items() if fact.get('bmr'))
        if bmr_id:
            self.retract(bmr_id)
        self.declare(Fact(bmr=updatedBMR))  # Update the BMR fact with the activity factor

    # Rule 7: If the user has not provided their glucose level, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(glucose_level=W())), salience=400)
    def ask_glucose_level(self):
        glucose_level = input("What is your glucose level? ")
        self.declare(Fact(glucose_level=float(glucose_level)))
        action_id = next(factId for factId, fact in self.facts.items() if fact.get('action'))
        if action_id:
            self.retract(action_id)
        self.declare(Fact(action="suggest_plan")) # update the action fact

    def printFact(self):
        print(self.facts.items())

if __name__ == "__main__":
    engine = DiabetesExpert()
    engine.reset()  # Prepare the engine for a new session
    engine.run()  # Run the engine to trigger rules
    engine.printFact()
    print("Diagnosis complete")
