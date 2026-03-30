import { GoogleGenAI } from "@google/genai";

// This service file is prepared for future AI integration (e.g., a chatbot helper for the app).
// Currently, the landing page does not require active API calls.

const apiKey = process.env.API_KEY || '';

// Example function structure for future use
export const getAIResponse = async (prompt: string) => {
  if (!apiKey) {
    console.warn("API Key not found");
    return null;
  }
  
  try {
    const ai = new GoogleGenAI({ apiKey });
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
    });
    return response.text;
  } catch (error) {
    console.error("Error fetching AI response:", error);
    return null;
  }
};