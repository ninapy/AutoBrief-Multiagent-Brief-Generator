import logging
from typing import List, Dict, Optional
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

class MeetingSchedulerAgent:
    def __init__(self):
        self.mock_teams_domain = "https://teams.microsoft.com/l/meetup-join/"
    
    def schedule_meetings_fast(self, brief_content: str, team_members: List[TeamMember]) -> List[Meeting]:
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
        Analyze this brief and generate a complete meeting schedule. Choose attendees from the available team based on their
        role and department's relevance to the project needs mentioned in the brief
        
        BRIEF:
        {brief_content}
        
        AVAILABLE TEAM:
        {chr(10).join(team_summary)}
        
        Generate a JSON response with this exact structure:
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
                    "attendee_indices": [0, 1, 2],
                    "title": "Meeting Title",
                    "agenda_bullets": ["Point 1", "Point 2", "Point 3"],
                    "duration_minutes": 60,
                    "timing": "asap|2_days|1_week"
                }}
            ]
        }}
        
        Rules:
        - Select 2-5 meetings based on brief complexity
        - Choose attendees from the team list by their job title's relevance to the project need
        - Keep agendas focused (3-5 bullets)
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500  # Increased for full response
            )
            
            # Parse response
            ai_response = json.loads(response['choices'][0]['message']['content'])
            
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
            
            return meetings
            
        except Exception as e:
            logging.error(f"Error in optimized scheduler: {e}")
            # Fallback to basic meeting
            return self._create_fallback_meeting(team_members[:3], brief_content)
    
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
