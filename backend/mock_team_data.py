# mock_team_data.py
from agents.meeting_scheduler_agent import TeamMember

# Mock EdgeVerve AI team for demo
EDGEVERVE_TEAM = [
    # Executive Leadership
    TeamMember(
        name="David Park",
        email="david.park@edgeverve.ai",
        role="VP of Marketing",
        department="Marketing",
        specialties=["strategic_planning", "executive_approval", "budget_approval"]
    ),
    TeamMember(
        name="Sarah Chen",
        email="sarah.chen@edgeverve.ai", 
        role="Chief Marketing Officer",
        department="Marketing",
        specialties=["brand_strategy", "executive_approval", "market_positioning"]
    ),
    
    # Marketing Team
    TeamMember(
        name="Jessica Rodriguez",
        email="jessica.rodriguez@edgeverve.ai",
        role="Brand Manager",
        department="Marketing",
        specialties=["brand_consistency", "messaging", "brand_guidelines"]
    ),
    TeamMember(
        name="Michael Thompson",
        email="michael.thompson@edgeverve.ai",
        role="Digital Marketing Manager",
        department="Marketing", 
        specialties=["social_media", "digital_campaigns", "analytics"]
    ),
    TeamMember(
        name="Amanda Foster",
        email="amanda.foster@edgeverve.ai",
        role="Content Marketing Manager",
        department="Marketing",
        specialties=["content_strategy", "copywriting", "blog_management"]
    ),g
    
    # Creative/Design Team
    TeamMember(
        name="Alex Kim",
        email="alex.kim@edgeverve.ai",
        role="Creative Director",
        department="Design",
        specialties=["creative_direction", "visual_design", "campaign_concepts"]
    ),
    TeamMember(
        name="Maya Patel",
        email="maya.patel@edgeverve.ai",
        role="Senior Graphic Designer",
        department="Design",
        specialties=["graphic_design", "visual_assets", "brand_materials"]
    ),
    TeamMember(
        name="Chris Johnson",
        email="chris.johnson@edgeverve.ai",
        role="Video Producer",
        department="Design",
        specialties=["video_production", "multimedia", "storytelling"]
    ),
    
    # Product Team
    TeamMember(
        name="Ryan Walsh",
        email="ryan.walsh@edgeverve.ai",
        role="Product Marketing Manager",
        department="Product",
        specialties=["product_messaging", "go_to_market", "feature_launches"]
    ),
    TeamMember(
        name="Lisa Park",
        email="lisa.park@edgeverve.ai",
        role="Product Manager",
        department="Product",
        specialties=["product_strategy", "user_experience", "technical_requirements"]
    ),
    
    # Sales Team
    TeamMember(
        name="Robert Martinez",
        email="robert.martinez@edgeverve.ai",
        role="Sales Director",
        department="Sales",
        specialties=["sales_enablement", "customer_insights", "market_feedback"]
    ),
    TeamMember(
        name="Jennifer Lee",
        email="jennifer.lee@edgeverve.ai",
        role="Sales Operations Manager",
        department="Sales",
        specialties=["sales_tools", "process_optimization", "data_analysis"]
    ),
    
    # Communications/PR
    TeamMember(
        name="Daniel Brown",
        email="daniel.brown@edgeverve.ai",
        role="Communications Manager",
        department="Marketing",
        specialties=["public_relations", "media_relations", "crisis_communication"]
    ),
    
    # Operations
    TeamMember(
        name="Sophie Wilson",
        email="sophie.wilson@edgeverve.ai",
        role="Marketing Operations Manager", 
        department="Marketing",
        specialties=["campaign_operations", "marketing_automation", "data_management"]
    ),
    
    # External Stakeholders (for comprehensive planning)
    TeamMember(
        name="External Agency",
        email="contact@creativepartners.com",
        role="External Creative Agency",
        department="External",
        specialties=["external_creative", "specialized_campaigns", "additional_resources"]
    )
]

# Helper function to get team members by department
def get_team_by_department(department: str):
    return [member for member in EDGEVERVE_TEAM if member.department.lower() == department.lower()]

# Helper function to get team members by specialty
def get_team_by_specialty(specialty: str):
    return [member for member in EDGEVERVE_TEAM 
            if member.specialties and specialty in member.specialties]

# Helper function to get executives
def get_executives():
    executive_roles = ["VP", "Chief", "Director"]
    return [member for member in EDGEVERVE_TEAM 
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
        for member in EDGEVERVE_TEAM
    ]