import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

def get_docker_logs(tail=150):
    try:
        result = subprocess.run(
            ["docker", "compose", "logs", "--tail", str(tail)], 
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except FileNotFoundError:
        print("[-] Docker command not found.")
        return ""
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to fetch logs: {e}")
        return ""

def analyze_incident(log_data):
    if not log_data.strip():
        print("[-] No logs available.")
        return

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY missing in .env")
        exit(1)

    print("[*] Processing system logs...")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    system_prompt = """
You are a Lead Site Reliability Engineer tasked with performing a comprehensive incident analysis based on raw server logs. Your objective is to generate a detailed and actionable Incident Response Report.

**Log Sources for Analysis:**
Review the provided Nginx, Flask/Gunicorn, and PostgreSQL logs. Assume these logs represent a recent, critical operational period.

**Key Areas for Identification and Analysis:**
For each identified incident or observation, provide specific examples from the logs (if available) and quantify the occurrences where possible.

1.  **Nginx Rate Limiting (HTTP 503 - Service Unavailable):**
    *   Identify instances of Nginx actively mitigating potential DDoS attacks or brute-force attempts through rate limiting.
    *   Quantify the frequency and duration of these events.
    *   Assess the effectiveness of the mitigation and any observed impact on legitimate traffic.

2.  **RASP Middleware Detections (HTTP 403 - Forbidden):**
    *   Detect and categorize blocks by Runtime Application Self-Protection (RASP) middleware, indicating attempts at XSS, SQL Injection, Path Traversal, or other OWASP Top 10 vulnerabilities.
    *   Provide specific attack patterns or payload examples from the logs.
    *   Evaluate the RASP's performance in preventing successful exploitation.

3.  **Database Constraint Violations (HTTP 409 - Conflict):**
    *   Identify occurrences of database errors related to constraint violations (e.g., unique key violations, foreign key failures), typically reflecting business logic validation issues or race conditions.
    *   Analyze the associated application requests and potential root causes.
    *   Quantify the frequency of these errors.

4.  **General System Health and Successful Operations (HTTP 200/201):**
    *   Summarize the overall health of the system, noting periods of stable operation and successful request processing.
    *   Highlight any significant patterns or anomalies in successful requests.

**Incident Response Report Structure and Content:**
Format the report in clean Markdown, adhering to the following sections. Ensure the tone is clinical, objective, and highly technical, suitable for an SRE team and management.

*   **📌 Executive Summary:**
    *   Provide a concise overview of the incident, including key findings, overall system status, and the most critical issues identified.
    *   State the perceived severity and potential business impact.

*   **⚙️ Threat Assessment:**
    *   Detail all identified security-related incidents (Nginx rate limiting, RASP blocks).
    *   Describe the nature of the threats, attack vectors, and the frequency of attempts.
    *   Include specific log snippets or patterns as evidence.

*   **📊 Defense Performance:**
    *   Evaluate the effectiveness of existing defense mechanisms (Nginx rate limiting, RASP).
    *   Discuss any observed limitations or areas where defenses were challenged.
    *   Provide metrics on blocked vs. successful malicious attempts.

*   **📈 Operational Insights:**
    *   Present findings related to application and database health, including successful operations and constraint violations.
    *   Analyze trends, anomalies, and potential performance bottlenecks.
    *   Include relevant log excerpts for clarity.

*   **📉 Recommendations:**
    *   Propose specific, actionable recommendations for immediate remediation and long-term prevention.
    *   Prioritize recommendations based on severity and impact.
    *   Suggest improvements to monitoring, alerting, and defense configurations.
    *   Include recommendations for further investigation if necessary.

**Instructions for LLM:**
*   Extract and synthesize information directly from the provided `Logs:` section.
*   Quantify observations wherever possible (e.g., "X occurrences of HTTP 503").
*   Use Markdown formatting consistently, including code blocks for log snippets.
*   Maintain a professional, data-driven narrative throughout the report.
    """
    
    full_prompt = f"{system_prompt}\n\nLogs:\n{log_data}"
    
    try:
        response = model.generate_content(full_prompt)
        print("\n--- SRE INCIDENT REPORT ---")
        print(response.text)
        print("---------------------------\n")
    except Exception as e:
        print(f"[-] Analysis failed: {e}")

if __name__ == "__main__":
    recent_logs = get_docker_logs()
    analyze_incident(recent_logs)
