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
        self.gender = input("What is your gender? Female/Male: ")  # Ask for the user's gender
        self.declare(Fact(gender=self.gender.strip().lower()))  # Store the gender as a fact

    # Rule 2: If the user has not provided their age, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(age=W())), salience=900)
    def ask_age(self):
        self.age = input("What is your age? ") 
        self.declare(Fact(age=int(self.age)))  # Store age as a fact

    # Rule 3: If the user has not provided their weight, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(weight=W())), salience=800)
    def ask_weight(self):
        self.weight = input("What is your weight in kilograms? ")
        self.declare(Fact(weight=float(self.weight)))  # Store weight as a fact

    # Rule 4: If the user has not provided their height, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(height=W())), salience=700)
    def ask_height(self):
        self.height = input("What is your height in centimeters? ")
        self.declare(Fact(height=float(self.height)))  # Store height as a fact

    # Rule 5: Calculate BMR once all data is collected
    @Rule(Fact(action="collect_data"), Fact(gender=W()), Fact(age=W()), Fact(weight=W()), Fact(height=W()), salience=600)
    def calculate_bmr(self):
        bmr = 0
        if self.gender == 'female':
            bmr = 10 * float(self.weight) + 6.25 * float(self.height) - 5 * int(self.age) - 161
        else:
            bmr = 10 * float(self.weight) + 6.25 * float(self.height) - 5 * int(self.age) + 5
        self.declare(Fact(bmr=float(bmr)))  # Store BMR as a fact
        print(f"Your BMR is: {bmr}")

    # Rule 6: If the user has not provided their activity level, ask for it
    @Rule(Fact(action="collect_data"), NOT(Fact(activity_level=W())), salience=500)
    def ask_activity_level(self):
        self.activity_level = input("What is your activity level? (sedentary, lightly active, moderately active, very active): ")
        self.declare(Fact(activity_level=self.activity_level.strip().lower()))  # Store activity level as a fact
        self.modify(Fact(action="collect_data"), action="suggest_plan") # update the action fact



if __name__ == "__main__":
    engine = DiabetesExpert()
    engine.reset()  # Prepare the engine for a new session
    engine.run()  # Run the engine to trigger rules
    print("Diagnosis complete")
