from compare_traffic import fetch_traffic_data, generate_llm_comparison_insights
from traffic import get_traffic_history
def compare_traffic(website1,website2):
    history1, data1 = fetch_traffic_data(website1)
    history2, data2 = fetch_traffic_data(website2)

    insights = generate_llm_comparison_insights(data1, data2, website1, website2)
    print("WEBSITE 1")
    print(history1)
    print("WEBSITE 2")
    print(history2)

compare_traffic("engine.com.pk", "equatorstores.com")
                
history1, data1 = get_traffic_history("engine.com.pk")
    
print("WEBSITE 3:")
print(history1)