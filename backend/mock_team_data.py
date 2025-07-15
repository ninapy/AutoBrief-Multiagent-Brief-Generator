# mock_team_data.py
from agents.meeting_scheduler_agent import TeamMember

# Mock Infosys team for demo
INFOSYS_TEAM = [
    # Executive Leadership
    TeamMember(
        name="Nina Py",
        email="nina.py@infosys.com", 
        role="VP Marketing - Americas",
        department="Marketing",
        specialties=["regional_strategy", "executive_approval", "market_positioning"]
    ),
    TeamMember(
        name="Julius Trubel",
        email="julius.trubel@infosys.com",
        role="VP Marketing - APAC",
        department="Marketing",
        specialties=["regional_strategy", "executive_approval", "emerging_markets"]
    ),
    
    # Global Marketing Team
    TeamMember(
        name="Avni Hulyalkar",
        email="avni.hulyalkar@infosys.com",
        role="Global Brand Manager",
        department="Marketing",
        specialties=["brand_consistency", "messaging", "brand_guidelines"]
    ),
    TeamMember(
        name="Michael Thompson",
        email="michael.thompson@infosys.com",
        role="Head of Digital Marketing",
        department="Marketing", 
        specialties=["digital_campaigns", "social_media", "marketing_automation"]
    ),
    TeamMember(
        name="David Park",
        email="david.park@infosys.com",
        role="Chief Marketing Officer",
        department="Marketing",
        specialties=["strategic_planning", "executive_approval", "global_campaigns"]
    ),
    TeamMember(
        name="Amanda Foster",
        email="amanda.foster@infosys.com",
        role="Global Content Strategy Director",
        department="Marketing",
        specialties=["content_strategy", "thought_leadership", "analyst_relations"]
    ),
    
    # Creative/Design Team
    TeamMember(
        name="Alex Kim",
        email="alex.kim@infosys.com",
        role="Global Creative Director",
        department="Creative",
        specialties=["creative_direction", "visual_design", "campaign_concepts"]
    ),
    TeamMember(
        name="Maya Patel",
        email="maya.patel@infosys.com",
        role="Senior Brand Designer",
        department="Creative",
        specialties=["graphic_design", "visual_assets", "brand_materials"]
    ),
    TeamMember(
        name="Chris Johnson",
        email="chris.johnson@infosys.com",
        role="Video Production Manager",
        department="Creative",
        specialties=["video_production", "multimedia", "digital_storytelling"]
    ),
    
    # Industry & Solutions Marketing
    TeamMember(
        name="Ryan Walsh",
        email="ryan.walsh@infosys.com",
        role="Industry Marketing Director - Financial Services",
        department="Marketing",
        specialties=["industry_messaging", "sector_expertise", "client_case_studies"]
    ),
    TeamMember(
        name="Lisa Park",
        email="lisa.park@infosys.com",
        role="Solutions Marketing Manager - AI & Automation",
        department="Marketing",
        specialties=["solution_positioning", "technical_messaging", "product_marketing"]
    ),
    
    # Communications & PR
    TeamMember(
        name="Daniel Brown",
        email="daniel.brown@infosys.com",
        role="Global Communications Director",
        department="Communications",
        specialties=["public_relations", "crisis_communication", "media_relations"]
    ),
    TeamMember(
        name="Priya Sharma",
        email="priya.sharma@infosys.com",
        role="Internal Communications Manager",
        department="Communications",
        specialties=["employee_communications", "change_management", "internal_campaigns"]
    ),
    
    # Sales Enablement & Operations
    TeamMember(
        name="Robert Martinez",
        email="robert.martinez@infosys.com",
        role="Global Sales Enablement Director",
        department="Sales",
        specialties=["sales_enablement", "training_materials", "competitive_intelligence"]
    ),
    TeamMember(
        name="Sophie Wilson",
        email="sophie.wilson@infosys.com",
        role="Marketing Operations Director", 
        department="Marketing",
        specialties=["campaign_operations", "marketing_automation", "data_analytics"]
    ),
    
    # Legal & Compliance
    TeamMember(
        name="Jennifer Lee",
        email="jennifer.lee@infosys.com",
        role="Legal Counsel - Marketing",
        department="Legal",
        specialties=["legal_review", "compliance", "risk_management"]
    ),
    
    # External Partners
    TeamMember(
        name="External Agency Lead",
        email="contact@globalcreative.com",
        role="External Creative Partner",
        department="External",
        specialties=["external_creative", "specialized_campaigns", "additional_resources"]
    )
]

# Helper function to get team members by department
def get_team_by_department(department: str):
    return [member for member in INFOSYS_TEAM if member.department.lower() == department.lower()]

# Helper function to get team members by specialty
def get_team_by_specialty(specialty: str):
    return [member for member in INFOSYS_TEAM 
            if member.specialties and specialty in member.specialties]

# Helper function to get executives
def get_executives():
    executive_roles = ["VP", "Chief", "Director", "Head of"]
    return [member for member in INFOSYS_TEAM 
            if any(role in member.role for role in executive_roles)]

# For API endpoint - return as JSON-serializable format
def get_team_data_json():
    return [
        {
            "name": member.name,
            "email": member.email, 
            "role": member.role,
            "department": member.department,
            "specialties": member.specialties or []
        }
        for member in INFOSYS_TEAM
    ]