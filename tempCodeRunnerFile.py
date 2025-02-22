def group_texts_by_label(data):
#     if isinstance(data, str):
#         data = json.loads(data)
    
#     grouped_data = {}
#     for item in data:
#         label = item.get('label')
#         text = item.get('text')

#         # Initialize an array for the label if it doesn't exist
#         if label not in grouped_data:
#             grouped_data[label] = []
#         # Append the text to the label's array
#         grouped_data[label].append(text)

#     return grouped_data