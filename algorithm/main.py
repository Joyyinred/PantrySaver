import time
import worker

def run_algorithm(how_frequent: int = 60):
    print()
    print("running algorithm...")
    print(f"checking every {how_frequent} seconds")
    
    while True:
        modified_households = worker.get_modified_households()
        
        if modified_households:
            for household_id in modified_households:
                worker.process_household_behavior(household_id)
        
        time.sleep(how_frequent)

if __name__ == "__main__":
    run_algorithm()