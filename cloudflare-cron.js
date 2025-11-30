export default {
  async scheduled(event, env, ctx) {
    // 替换为你的 Vercel 项目地址
    const TARGET_URL = "https://your-vercel-project.vercel.app/api/collect";
    
    console.log(`Triggering collection at ${new Date().toISOString()}`);
    
    try {
      const response = await fetch(TARGET_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "Cloudflare-Cron/1.0"
        },
        body: JSON.stringify({
          subreddits: [
            "Entrepreneur", 
            "SaaS", 
            "Smallbusiness", 
            "InternetIsBeautiful", 
            "Startups", 
            "NoCode"
          ],
          limit: 100 // 每次采集数量
        })
      });
      
      const text = await response.text();
      console.log(`Response status: ${response.status}`);
      console.log(`Response body: ${text.slice(0, 200)}...`);
      
    } catch (error) {
      console.error("Error triggering collection:", error);
    }
  },

  async fetch(request, env, ctx) {
    return new Response("Cron Worker is running. Set up a trigger in Cloudflare Dashboard.", {
      status: 200
    });
  }
};
