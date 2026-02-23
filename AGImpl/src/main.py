from .graph import create_graph
from .models import Briefcase

def main():
    app = create_graph()
    
    # Initialize state with an S3 path
    initial_state = Briefcase(s3_path="s3://loyalty-bucket/applications/app_001.jpg")
    
    print("Starting LangGraph Workflow...")
    final_state = app.invoke(initial_state)
    
    print("\n--- Final Briefcase State ---")
    print(f"Name: {final_state['name']}")
    print(f"Income: ${final_state['income']}")
    print(f"Loyalty Tier: {final_state['loyalty_tier']}")
    print(f"Base APR: {final_state['base_apr']}%")
    print(f"Final APR: {final_state['final_apr']}%")

if __name__ == "__main__":
    main()
