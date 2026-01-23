// api/analyze-job.js
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { job, resumeSummary } = req.body;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY, // API key stored securely
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{
          role: 'user',
          content: `You are a job matching expert. Analyze this job against the candidate's resume.

RESUME SUMMARY:
- Persona: ${resumeSummary.persona}
- Seniority: ${resumeSummary.seniority}
- Key Skills: ${resumeSummary.keywords.join(", ")}

JOB DETAILS:
- Title: ${job.title}
- Company: ${job.company}
- Role Category: ${job.role || "Not specified"}
- Location: ${job.location}

Respond ONLY with a JSON object (no markdown, no backticks):
{
  "score": <number 0-100>,
  "reason": "<5-7 word explanation>",
  "insights": "<1 sentence about why this match works or doesn't>"
}

Consider:
1. Does the job title align with their persona and seniority?
2. For PM roles: look for product area fit
3. For similar seniority levels, differentiate based on role specificity
4. Company reputation and role scope matter
5. Give varied scores - don't rate everything the same!`
        }]
      })
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('Anthropic API Error:', error);
      return res.status(response.status).json({ error: 'API request failed' });
    }

    const data = await response.json();
    const text = data.content?.find(c => c.type === 'text')?.text || '{}';
    const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    const result = JSON.parse(cleanText);

    return res.status(200).json({
      score: Math.min(100, Math.max(0, result.score || 50)),
      reason: result.reason || 'AI match analysis',
      insights: result.insights || ''
    });

  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error.message 
    });
  }
}
