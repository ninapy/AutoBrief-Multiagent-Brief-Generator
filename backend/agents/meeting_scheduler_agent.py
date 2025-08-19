import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass, asdict

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger(__name__)

@dataclass
class TeamMember:
    name: str
    email: str
    role: str
    department: str
    specialties: List[str] = None

@dataclass
class Meeting:
    title: str
    attendees: List[str]  # email addresses
    attendee_names: List[str]  # names for personal touch
    attendee_roles: List[str]  # job titles for context
    attendee_departments: List[str]  # departments for structure
    suggested_time: str
    duration_minutes: int
    teams_link: str
    agenda: str
    meeting_type: str
    priority: str

@dataclass
class Action:
    task: str
    assignee_name: List[str]
    assignee_role: List[str] 
    assignee_departments: List[str]
    priority: str  # "high", "medium", "low"
    deadline: str  # "1_day", "3_days", "1_week", "2_weeks"
    category: str  # "research", "design", "content", "approval", "logistics"
    dependencies: List[str]
    deliverable: str

class MeetingSchedulerAgent:
    def __init__(self):
        self.mock_teams_domain = "https://teams.microsoft.com/l/meetup-join/"
    
    def schedule_meetings_fast(self, brief_content: str, team_members: List[TeamMember]):
        """
        Schedule meetings based off brief
        """
        # Create team summary for AI
        team_summary = []
        for i, member in enumerate(team_members):
            specialties = ", ".join(member.specialties) if member.specialties else "General"
            team_summary.append(f"{i}: {member.name} - {member.role} ({member.department}) - {specialties}")
        
        # Single comprehensive prompt
        prompt = f"""
        You are a meeting scheduler. Based on the brief content, create a JSON response with suggested meetings.
        
        BRIEF:
        {brief_content}
        
        AVAILABLE TEAM:
        {chr(10).join(team_summary)}
        
        IMPORTANT: Respond ONLY with valid JSON in this exact format:
        {{
            "project_analysis": {{
                "urgency": "high|medium|low",
                "complexity": "high|medium|low", 
                "key_requirements": ["brand_work", "creative_design", "executive_approval"]
            }},
            "meetings": [
                {{
                    "type": "kickoff|creative_review|approval|status_update",
                    "priority": "high|medium|low",
                    "attendee_indices": [0, 1, 2, etc],
                    "title": "Meeting Title",
                    "agenda_bullets": ["Point 1", "Point 2", "Point 3", etc],
                    "duration_minutes": 30|60|90|120,
                    "timing": "asap|2_days|1_week"
                }}
            ]
            "actionable_items": [
                {{
                    "task": "Task description",
                    "assignee_index": 0,
                    "priority": "high|medium|low",
                    "deadline": "1_day|3_days|1_week|2_weeks",
                    "category": "research|design|content|approval|logistics",
                    "dependencies": ["Optional task dependencies"],
                    "deliverable": "What needs to be produced"
                }}
            ]
        }}
        
        Rules:
        - Select 2-5 meetings based on brief complexity
        - Choose attendees from the team list by their job title's relevance to the project need and identify them by their indices
        - Keep agendas focused (3-5 bullets)
        - Generate 3-8 actionable items that support the project goals
        - Assign tasks to team members based on their expertise
        - Include pre-meeting preparation tasks
        - Prioritize items that unblock other work
        - Consider content creation, approvals, and logistics
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
                max_tokens=1500  # Increased for full response
            )
            
            # Parse response
            ai_response = json.loads(response.choices[0].message.content)
            
            # Convert to Meeting objects
            meetings = []
            for meeting_data in ai_response['meetings']:
                # Get selected team members
                selected_members = [team_members[i] for i in meeting_data['attendee_indices'] 
                                  if i < len(team_members)]
                
                if not selected_members:
                    continue
                
                # Create meeting object
                meeting = Meeting(
                    title=meeting_data['title'],
                    attendees=[m.email for m in selected_members],
                    attendee_names=[m.name for m in selected_members],
                    attendee_roles=[m.role for m in selected_members],
                    attendee_departments=[m.department for m in selected_members],
                    suggested_time=self._calculate_time_fast(meeting_data['timing'], meeting_data['priority']),
                    duration_minutes=meeting_data['duration_minutes'],
                    teams_link=self._generate_teams_link(),
                    agenda="\n".join([f"• {bullet}" for bullet in meeting_data['agenda_bullets']]),
                    meeting_type=meeting_data['type'],
                    priority=meeting_data['priority']
                )
                meetings.append(meeting)
            
            # Convert to Actionable item objects
            actions = []
            for action_data in ai_response['actionable_items']:
                assignee = team_members[action_data['assignee_index']]
                
                # Create meeting object
                action = Action(
                    task=action_data['task'],
                    assignee_name=[assignee.name],
                    assignee_role=[assignee.role],
                    assignee_departments=[assignee.department],
                    priority=action_data['priority'],
                    deadline=action_data['deadline'],
                    category=action_data['category'],
                    dependencies=action_data['dependencies'],
                    deliverable=action_data['deliverable']
                )
                actions.append(action)
            
            return meetings, actions
            
        except Exception as e:
            logging.error(f"Error in optimized scheduler: {e}")
            fallback_meetings = self._create_fallback_meeting(team_members[:3], brief_content)
            fallback_actions = []
            return fallback_meetings, fallback_actions

    
    def _calculate_time_fast(self, timing: str, priority: str) -> str:
        """Fast time calculation without complex logic"""
        from datetime import datetime, timedelta
        
        base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        if timing == "asap":
            days = 1
        elif timing == "2_days":
            days = 2
        elif timing == "1_week":
            days = 7
        else:
            days = 3
        
        meeting_time = base_time + timedelta(days=days)
        return meeting_time.isoformat()
    
    def _generate_teams_link(self) -> str:
        """Generate mock Teams link"""
        import uuid
        return f"{self.mock_teams_domain}{str(uuid.uuid4())[:12]}"
    
    def _create_fallback_meeting(self, attendees: List[TeamMember], brief: str) -> List[Meeting]:
        """Simple fallback if AI fails"""
        return [Meeting(
            title="Project Kickoff Meeting",
            attendees=[m.email for m in attendees],
            attendee_names=[m.name for m in attendees],
            attendee_roles=[m.role for m in attendees], 
            attendee_departments=[m.department for m in attendees],
            suggested_time=self._calculate_time_fast("2_days", "medium"),
            duration_minutes=60,
            teams_link=self._generate_teams_link(),
            agenda="• Review project requirements\n• Discuss timeline\n• Assign responsibilities",
            meeting_type="kickoff",
            priority="medium"
        )]

# Helper function to convert meetings to dict for JSON response
def meetings_to_dict(meetings: List[Meeting]) -> List[Dict]:
    """Convert Meeting objects to dictionaries for API response"""
    return [asdict(meeting) for meeting in meetings]

def actions_to_dict(actions: List[Action]) -> List[Dict]:
    """Convert Meeting objects to dictionaries for API response"""
    return [asdict(action) for action in actions]