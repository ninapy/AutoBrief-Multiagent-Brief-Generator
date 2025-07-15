import openai
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass, asdict

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
    attendee_names: List[str]  # for display
    suggested_time: str
    duration_minutes: int
    teams_link: str
    agenda: str
    meeting_type: str
    priority: str  # "high", "medium", "low"

class MeetingSchedulerAgent:
    def __init__(self):
        self.mock_teams_domain = "https://teams.microsoft.com/l/meetup-join/"
    
    def generate_teams_link(self) -> str:
        """Generate a mock Teams meeting link for demo purposes"""
        meeting_id = str(uuid.uuid4())[:12]
        return f"{self.mock_teams_domain}{meeting_id}"
    
    def analyze_brief_requirements(self, brief_content: str) -> Dict:
        """
        Use LLM to analyze the creative brief and identify what types of meetings/people are needed
        """
        prompt = f"""
        Analyze this creative brief and identify what types of meetings and stakeholders are needed.
        
        Brief Content:
        {brief_content}
        
        Please identify:
        1. Key project requirements (brand work, design, approval, technical, etc.)
        2. Timeline urgency (rushed, normal, flexible)
        3. Stakeholder types needed (executives, creative team, product team, etc.)
        4. Meeting types required (kickoff, reviews, approvals, etc.)
        
        Return a JSON response with this structure:
        {{
            "project_requirements": ["brand_consistency", "creative_design", "executive_approval"],
            "timeline_urgency": "normal",
            "stakeholder_types": ["brand_manager", "creative_director", "vp_marketing"],
            "meeting_types": [
                {{
                    "type": "kickoff",
                    "priority": "high",
                    "stakeholders": ["brand_manager", "creative_director"],
                    "timing": "asap"
                }}
            ]
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # Parse the JSON response
            analysis = json.loads(response['choices'][0]['message']['content'])
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing brief: {e}")
            # Fallback basic analysis
            return {
                "project_requirements": ["creative_design", "brand_consistency"],
                "timeline_urgency": "normal",
                "stakeholder_types": ["creative_director", "brand_manager"],
                "meeting_types": [
                    {
                        "type": "kickoff",
                        "priority": "high",
                        "stakeholders": ["creative_director", "brand_manager"],
                        "timing": "asap"
                    }
                ]
            }
    
    def match_team_members(self, team_members: List[TeamMember], requirements: Dict) -> Dict[str, List[TeamMember]]:
        """
        Match team members to project requirements using LLM
        """
        # Create a summary of available team members
        team_summary = []
        for member in team_members:
            specialties_str = ", ".join(member.specialties) if member.specialties else "General"
            team_summary.append(f"{member.name} - {member.role} ({member.department}) - {specialties_str}")
        
        team_list = "\n".join(team_summary)
        requirements_str = json.dumps(requirements, indent=2)
        
        prompt = f"""
        Given this team roster and project requirements, select the best team members for each meeting type.
        
        Available Team Members:
        {team_list}
        
        Project Requirements:
        {requirements_str}
        
        For each meeting type mentioned in the requirements, select the most relevant team members.
        Consider:
        - Role relevance to the project needs
        - Department alignment
        - Specialties matching requirements
        - Meeting type (kickoff needs broader group, reviews need specialists)
        
        Return JSON with meeting types as keys and selected email addresses as values:
        {{
            "kickoff": ["email1@company.com", "email2@company.com"],
            "creative_review": ["email3@company.com"],
            "approval": ["email4@company.com"]
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            matches = json.loads(response['choices'][0]['message']['content'])
            
            # Convert email addresses back to TeamMember objects
            email_to_member = {member.email: member for member in team_members}
            result = {}
            
            for meeting_type, emails in matches.items():
                result[meeting_type] = [email_to_member[email] for email in emails if email in email_to_member]
            
            return result
        
        except Exception as e:
            logger.error(f"Error matching team members: {e}")
            # Fallback - return basic matches
            return {"kickoff": team_members[:3]}
    
    def generate_meeting_details(self, meeting_type: str, attendees: List[TeamMember], 
                               brief_content: str, priority: str = "medium") -> Meeting:
        """
        Generate specific meeting details including agenda
        """
        attendee_emails = [member.email for member in attendees]
        attendee_names = [member.name for member in attendees]
        
        # Generate agenda based on meeting type and brief
        agenda_prompt = f"""
        Create a focused meeting agenda for a {meeting_type} meeting about this creative brief:
        
        Brief: {brief_content[:500]}...
        
        Attendees: {', '.join([f"{m.name} ({m.role})" for m in attendees])}
        
        Create a concise agenda (3-5 bullet points) that's specific to this project and meeting type.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": agenda_prompt}],
                temperature=0.4,
                max_tokens=200
            )
            agenda = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.warning(f"Could not generate agenda: {e}")
            agenda = f"Discuss {meeting_type} for creative project"
        
        # Determine meeting duration and timing
        duration_map = {
            "kickoff": 60,
            "creative_review": 45,
            "approval": 30,
            "status_update": 30,
            "final_review": 45
        }
        
        duration = duration_map.get(meeting_type, 45)
        
        # Calculate suggested time (for demo, use next business day)
        suggested_time = self._calculate_suggested_time(meeting_type, priority)
        
        # Generate meeting title
        title = self._generate_meeting_title(meeting_type, brief_content)
        
        return Meeting(
            title=title,
            attendees=attendee_emails,
            attendee_names=attendee_names,
            suggested_time=suggested_time,
            duration_minutes=duration,
            teams_link=self.generate_teams_link(),
            agenda=agenda,
            meeting_type=meeting_type,
            priority=priority
        )
    
    def _calculate_suggested_time(self, meeting_type: str, priority: str) -> str:
        """Calculate suggested meeting time based on type and priority"""
        now = datetime.now()
        
        # Priority-based scheduling
        if priority == "high":
            if meeting_type == "kickoff":
                # Schedule kickoff ASAP (next business day, 10 AM)
                days_ahead = 1
            else:
                days_ahead = 2
        elif priority == "medium":
            days_ahead = 3 if meeting_type == "kickoff" else 5
        else:  # low priority
            days_ahead = 7
        
        # Find next business day
        suggested_date = now + timedelta(days=days_ahead)
        while suggested_date.weekday() >= 5:  # Skip weekends
            suggested_date += timedelta(days=1)
        
        # Set time based on meeting type
        time_map = {
            "kickoff": 10,  # 10 AM
            "creative_review": 14,  # 2 PM  
            "approval": 11,  # 11 AM
            "status_update": 15,  # 3 PM
        }
        
        hour = time_map.get(meeting_type, 10)
        suggested_time = suggested_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        return suggested_time.isoformat()
    
    def _generate_meeting_title(self, meeting_type: str, brief_content: str) -> str:
        """Generate a specific meeting title based on the brief content"""
        # Extract key project info for title
        lines = brief_content.split('\n')[:5]  # First few lines usually have key info
        
        title_map = {
            "kickoff": "Campaign Kickoff",
            "creative_review": "Creative Review",
            "approval": "Executive Approval",
            "status_update": "Project Status Update",
            "final_review": "Final Review"
        }
        
        base_title = title_map.get(meeting_type, "Project Meeting")
        
        # Try to add project-specific context
        for line in lines:
            if "campaign" in line.lower():
                return f"{base_title} - Campaign Planning"
            elif "product" in line.lower():
                return f"{base_title} - Product Launch"
            elif "brand" in line.lower():
                return f"{base_title} - Brand Initiative"
        
        return base_title
    
    def schedule_meetings(self, brief_content: str, team_members: List[TeamMember]) -> List[Meeting]:
        """
        Main function to analyze brief and schedule appropriate meetings
        """
        logger.info("Starting meeting scheduling process...")
        
        # Step 1: Analyze what the brief requires
        requirements = self.analyze_brief_requirements(brief_content)
        logger.info(f"Brief analysis complete: {requirements['meeting_types']}")
        
        # Step 2: Match team members to requirements
        team_matches = self.match_team_members(team_members, requirements)
        logger.info(f"Team matching complete: {list(team_matches.keys())}")
        
        # Step 3: Generate meetings
        meetings = []
        for meeting_info in requirements['meeting_types']:
            meeting_type = meeting_info['type']
            priority = meeting_info.get('priority', 'medium')
            
            if meeting_type in team_matches:
                attendees = team_matches[meeting_type]
                meeting = self.generate_meeting_details(
                    meeting_type, attendees, brief_content, priority
                )
                meetings.append(meeting)
        
        logger.info(f"Generated {len(meetings)} meetings")
        return meetings


# Helper function to convert meetings to dict for JSON response
def meetings_to_dict(meetings: List[Meeting]) -> List[Dict]:
    """Convert Meeting objects to dictionaries for API response"""
    return [asdict(meeting) for meeting in meetings]