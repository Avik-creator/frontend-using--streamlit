from datetime import date,datetime
import re
import json

def skill_score(can_skills, job_req_skill):

  sum = 0
  for c in can_skills:
    for j in job_req_skill:
       if c == j :
          sum += 1
  skill_score = (sum/len(job_req_skill)) * 100
  return skill_score

def parse_date_range(date_range):
    # Split the date range into start and end parts
  if "-" in date_range:
    start_str, end_str = date_range.split(" - ")
    
    # Parse dates and format them
    start_date = month_from_name(start_str)
  else:
    start_date= month_from_name(date_range)
  try:
      end_date = month_from_name(end_str)
  except:
       end_date =  datetime.now()


  if (start_date.year> end_date.year)  or (start_date.year == end_date.year) and (start_date.month > end_date.month):
       temp = start_date
       start_date = end_date
       end_date = temp 
  return start_date,end_date

def calculate_duration(start_date,end_date): #Duration calculation in months
  months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
  return months + 1

def month_from_name(date_pass):
    dt = re.split(r"[ ./]", date_pass)
    if len(dt) == 1:
        d = date(int(date_pass),1,1)
    elif len(dt) == 2:
        try:
            int(dt[1]) and int(dt[0])
            if (int(dt[1])) > 12:
                d = date(int(dt[1][:4]),int(dt[0][:3]),1)
            else:
                d = date(int(dt[0][:4]),int(dt[1][:3]),1)
        except:
            try:
                int(dt[1])
                try:
                    # Full month name
                    m = datetime.strptime(dt[0], "%B").month
                    d = date(int(dt[1][:4]),m,1)
                except:
                    m = datetime.strptime(dt[0][:3], "%b").month  
                    d = date(int(dt[1][:4]),m,1)
            except:
                int(dt[0])   
                try:
                    m = datetime.strptime(dt[1], "%B").month# Full month name
                    d = date(int(dt[0][:4]),m,1)
                except:
                    m = datetime.strptime(dt[1][:3], "%b").month
                    d = date(int(dt[0][:4]),m,1)

    return d

def convert_to_months(duration_str):
  """Convert a duration string like '10 years 5 months' to total months."""
  years, months = 0, 0
    
  # Split the string into parts
  parts = duration_str.split()
    
  # Iterate through the parts to extract years and months
  for i in range(len(parts)):
      if parts[i] == "years":
          years = int(parts[i - 1])
      elif parts[i] == "months":
          months = int(parts[i - 1])

    # Calculate total months
  total_months = (years * 12) + months
  return total_months

def experience_score(job_req_exp,cand_exp,can_edu_tenure):
  # Calculate the number of months
  state = 0
  today_date= datetime.now()
  if can_edu_tenure:
    can_edu_start,can_edu_end= parse_date_range(can_edu_tenure)
    dur= calculate_duration(can_edu_end, today_date) 
    if dur <= 12:
      state = 1
    elif dur > 12 and dur <= 60:
      state = 2
    else:
      state = 3
    
  total_exp_in_months = 0
  for c in cand_exp:
    start_date,end_date = parse_date_range(c)
    months = calculate_duration(start_date,end_date)
    total_exp_in_months += months
  job_req_exp_months = convert_to_months(job_req_exp)
  
  if state == 0:
     if total_exp_in_months <= 12:state = 1
     elif total_exp_in_months<= 60 and total_exp_in_months>12 : state = 2
     else:state = 3
  if job_req_exp_months <= total_exp_in_months:
     print("Eligible for the role")
     return (100,state)
  else:
     print("Not eligible for the job, still required : " ,(job_req_exp_months - total_exp_in_months),"months of experience")
     return ((total_exp_in_months/job_req_exp_months)*100,state)

ABBREVIATIONS = {
    "Bachelor of Science": "B.Sc",
    "Bachelor of Arts": "B.A",
    "Bachelor of Engineering": "B.E",
    "Bachelor of Technology": "B.Tech",
    "Master of Science": "M.Sc",
    "Master of Arts": "M.A",
    "Master of Business Administration": "MBA",
    "Master of Technology": "M.Tech",
    "Doctor of Philosophy": "Ph.D",
    "Doctor of Medicine": "MD"
}

REVERSE_ABBREVIATIONS = {val: key for key, val in ABBREVIATIONS.items()}

BACHELOR_KEYWORDS = {"bachelor", "b.sc", "b.a", "b.e", "b.tech", "bba", "b.com", "bfa"}
POSTGRADUATE_KEYWORDS = {"master", "m.sc", "m.a", "mba", "m.tech", "m.e", "m.com", "llm", "ph.d", "md"}

def normalize_degree(degree):
    """Convert full degree names to abbreviations and normalize case (bi-directional)."""
    degree = degree.lower().strip()

    # Remove dots ("M.B.A" -> "MBA")
    degree = re.sub(r'\.', '', degree)

    # Replace full names with abbreviations
    for full, short in ABBREVIATIONS.items():
        degree = re.sub(full.lower(), short.lower(), degree)

    # Replace abbreviations with full names
    for short, full in sorted(REVERSE_ABBREVIATIONS.items(), key=lambda x: -len(x[0])):
        degree = re.sub(rf'\b{re.escape(short.lower())}\b(?!\w)', full.lower(), degree)    
    
    # Normalize general terms (handles variations like "Post Graduate", "Post-Graduate")
    degree = re.sub(r'post[-\s]?graduate', 'postgraduate', degree)  # Fixes "Post Graduate", "Post-Graduate"
    degree = re.sub(r'under[-\s]?graduate', 'undergraduate', degree)  # If needed

    return degree

def contains_keyword(degree, keywords):
    """Check if a normalized degree contains any of the specified keywords."""

    return any(keyword in degree for keyword in keywords)

def is_eligible(person_degrees, eligible_degrees):
    """Check if person is educationally eligible for the role"""

    person_degrees_normalized = {normalize_degree(degree) for degree in person_degrees}
    eligible_degrees_normalized = {normalize_degree(degree) for degree in eligible_degrees}

    print(person_degrees_normalized, eligible_degrees_normalized)

    # Check for direct match ...
    if not person_degrees_normalized.isdisjoint(eligible_degrees_normalized):
        return True  # Eligible

    # Check for partial match (substring matching) ...
    for person_degree in person_degrees_normalized:
        for eligible_degree in eligible_degrees_normalized:
            if re.search(rf'\b{re.escape(eligible_degree)}\b', person_degree):
                return True  # Eligible

    # Check for "Graduate" (Bachelor's or higher) ...
    if "graduate" in eligible_degrees_normalized or "undergraduate" in eligible_degrees_normalized:
        if any(contains_keyword(deg, BACHELOR_KEYWORDS | POSTGRADUATE_KEYWORDS) for deg in person_degrees_normalized):
            return True  # Eligible

    # Check for "Postgraduate" ...
    if "postgraduate" in eligible_degrees_normalized:
        if any(contains_keyword(deg, POSTGRADUATE_KEYWORDS) for deg in person_degrees_normalized):
            return True  # Eligible
        
    return False  # Not Eligible

def final_main(json_data):
  can_skills = []
  can_edu_tenure = None
  cand_exp = []
  cand_edu_deg = []
  for item in json_data['data']: #Applicant
    label = item['label']
    text = item['text']
    if "SKILL:" in label:
      can_skills.append(text) 
    elif "EDUCATION TENURE" in label:
        can_edu_tenure = text
    elif "WORK EXPERIENCE TENURE" in label:
      cand_exp.append(text)
    elif "EDUCATION DEGREE" in label:
      cand_edu_deg.append(text)
      
  #From API current job market
  job_req_skill= ["Python", "SQL", "Data Analysis", "Machine Learning","CSS","UI"] 
  job_req_exp = "10 years"
  job_req_edu = "Bachelor in IT"


  skill_score_per = skill_score(can_skills,job_req_skill)
  print(f"SKill Score: {skill_score_per}")

  exp_score,state = experience_score(job_req_exp,cand_exp,can_edu_tenure)
  print("Experience is matched by: ",exp_score)
  
  job_req_edu_list = job_req_edu.split(" ")
  print("Is eligible",is_eligible(cand_edu_deg, job_req_edu_list)) 
  if(is_eligible(cand_edu_deg, job_req_edu_list)):
    edu_score  = 100
  else:
    edu_score = 0
    
  if state == 0:#invalid case
     print("Experience level cannot be identified!")
     skill_contri = 0.5
     exp_contri = 0.4
     edu_contri = 0.1 
  elif state == 1:
     print("Fresher")
     skill_contri = 0.5
     exp_contri = 0.3
     edu_contri = 0.2 
  elif state == 2:
     print("Mid-level")
     skill_contri = 0.5
     exp_contri = 0.45
     edu_contri = 0.05
  else:
     print("Experienced")
     skill_contri = 0.4
     exp_contri = 0.55
     edu_contri = 0.05 
  
  final_score = (skill_contri * skill_score_per)+(exp_contri * exp_score)+(edu_contri * edu_score)
  print("The final score is: ",final_score)
  return final_score



if __name__ == "__main__":
  with open('myfile.json', 'r') as file:
    json_data = json.load(file)

  main(json_data)