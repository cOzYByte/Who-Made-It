import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import CountUp from "react-countup";
import { MagnifyingGlass, Lightbulb, TrendUp, Lightning, Trophy } from "@phosphor-icons/react";
import { toast, Toaster } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState({ total_queries: 0, men_count: 0, women_count: 0, milestones: [] });
  const [categories, setCategories] = useState([]);
  const [recentQueries, setRecentQueries] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [showFlash, setShowFlash] = useState(false);

  useEffect(() => {
    fetchStats();
    fetchCategories();
    fetchRecentQueries();
    fetchMilestones();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const fetchRecentQueries = async () => {
    try {
      const response = await axios.get(`${API}/queries?limit=10`);
      setRecentQueries(response.data);
    } catch (error) {
      console.error("Error fetching recent queries:", error);
    }
  };

  const fetchMilestones = async () => {
    try {
      const response = await axios.get(`${API}/milestones`);
      setMilestones(response.data);
    } catch (error) {
      console.error("Error fetching milestones:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) {
      toast.error("Please enter something to analyze");
      return;
    }

    setLoading(true);
    const oldMilestones = stats.milestones || [];
    
    try {
      const response = await axios.post(`${API}/analyze`, { input_text: inputText });
      setResult(response.data);
      
      setShowFlash(true);
      setTimeout(() => setShowFlash(false), 300);
      
      await fetchStats();
      fetchCategories();
      fetchRecentQueries();
      fetchMilestones();
      
      // Check if we hit a new milestone
      const newStats = await axios.get(`${API}/stats`);
      const newMilestones = newStats.data.milestones || [];
      if (newMilestones.length > oldMilestones.length) {
        const latestMilestone = newMilestones[newMilestones.length - 1];
        toast.success(`🎉 MILESTONE ACHIEVED: ${latestMilestone.toLocaleString()} queries!`, {
          duration: 5000,
        });
      }
      
      toast.success("Analysis complete!");
    } catch (error) {
      console.error("Error analyzing:", error);
      toast.error("Failed to analyze. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const menPercentage = stats.total_queries > 0 
    ? Math.round((stats.men_count / stats.total_queries) * 100) 
    : 0;
  const womenPercentage = stats.total_queries > 0 
    ? Math.round((stats.women_count / stats.total_queries) * 100) 
    : 0;

  return (
    <div className="min-h-screen noise-bg">
      <Toaster position="top-center" richColors />
      
      <AnimatePresence>
        {showFlash && result && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.3 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 pointer-events-none"
            style={{
              backgroundColor: result.result === 'man' ? '#002FA7' : result.result === 'woman' ? '#FF4500' : 'transparent'
            }}
          />
        )}
      </AnimatePresence>

      <div className="container mx-auto px-4 py-8 md:py-12 max-w-7xl">
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 md:mb-16"
        >
          <h1 
            className="font-syne font-extrabold text-6xl md:text-8xl lg:text-9xl mb-4"
            style={{ letterSpacing: '-0.02em' }}
            data-testid="main-heading"
          >
            WHO MADE IT?
          </h1>
          <p className="text-lg md:text-xl font-outfit text-muted-foreground max-w-2xl">
            Discover the gender of inventors, creators, and innovators behind products, services, and inventions.
          </p>
        </motion.header>

        <div className="grid lg:grid-cols-3 gap-8 mb-12">
          <div className="lg:col-span-2 space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <form onSubmit={handleSubmit} className="mb-8">
                <div className="relative" data-testid="search-form">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="iPhone"
                    className="massive-input text-foreground"
                    disabled={loading}
                    data-testid="search-input"
                  />
                  <button
                    type="submit"
                    className="brutalist-button bg-foreground text-background mt-6"
                    disabled={loading}
                    data-testid="search-button"
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        >
                          <Lightning size={20} weight="bold" />
                        </motion.div>
                        ANALYZING...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <MagnifyingGlass size={20} weight="bold" />
                        ANALYZE
                      </span>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>

            <AnimatePresence mode="wait">
              {result && (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3 }}
                  className="brutalist-card bg-card p-8"
                  data-testid="result-card"
                >
                  <div className="flex items-start gap-4 mb-6">
                    <div 
                      className="w-3 h-3 rounded-none mt-2"
                      style={{
                        backgroundColor: result.result === 'man' ? '#002FA7' : result.result === 'woman' ? '#FF4500' : '#808080'
                      }}
                    />
                    <div className="flex-1">
                      <h2 className="font-syne font-bold text-4xl md:text-6xl mb-2" data-testid="result-title">
                        {result.input_text}
                      </h2>
                      <p className="text-lg md:text-xl text-muted-foreground font-outfit uppercase tracking-wider">
                        {result.category}
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm font-outfit uppercase tracking-wider text-muted-foreground mb-1">
                        Created by
                      </div>
                      <div 
                        className="font-syne font-bold text-3xl md:text-4xl"
                        style={{
                          color: result.result === 'man' ? '#002FA7' : result.result === 'woman' ? '#FF4500' : 'inherit'
                        }}
                        data-testid="creator-name"
                      >
                        {result.creator_name}
                      </div>
                      <div className="text-xl font-outfit uppercase tracking-wider mt-1" data-testid="creator-gender">
                        ({result.result})
                      </div>
                    </div>
                    
                    {result.explanation && (
                      <div className="pt-4 border-t-2 border-current">
                        <p className="text-base md:text-lg font-outfit" data-testid="result-explanation">
                          {result.explanation}
                        </p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="space-y-8">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="brutalist-card bg-card p-8"
              data-testid="scoreboard"
            >
              <div className="flex items-center gap-2 mb-6">
                <TrendUp size={24} weight="bold" />
                <h3 className="font-syne font-bold text-2xl">SCOREBOARD</h3>
              </div>
              
              <div className="space-y-6">
                <div>
                  <div className="text-sm font-outfit uppercase tracking-wider text-muted-foreground mb-2">
                    Total Queries
                  </div>
                  <div className="font-syne font-bold text-5xl" data-testid="total-count">
                    <CountUp end={stats.total_queries} duration={1} />
                  </div>
                </div>
                
                <div className="h-px bg-border" />
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-outfit uppercase tracking-wider mb-2" style={{ color: '#002FA7' }}>
                      MEN
                    </div>
                    <div className="font-syne font-bold text-4xl" style={{ color: '#002FA7' }} data-testid="men-count">
                      <CountUp end={stats.men_count} duration={1} />
                    </div>
                    <div className="text-sm font-outfit mt-1 text-muted-foreground">
                      {menPercentage}%
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm font-outfit uppercase tracking-wider mb-2" style={{ color: '#FF4500' }}>
                      WOMEN
                    </div>
                    <div className="font-syne font-bold text-4xl" style={{ color: '#FF4500' }} data-testid="women-count">
                      <CountUp end={stats.women_count} duration={1} />
                    </div>
                    <div className="text-sm font-outfit mt-1 text-muted-foreground">
                      {womenPercentage}%
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            {categories.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="brutalist-card bg-card p-8"
                data-testid="categories-card"
              >
                <div className="flex items-center gap-2 mb-6">
                  <Lightbulb size={24} weight="bold" />
                  <h3 className="font-syne font-bold text-2xl">CATEGORIES</h3>
                </div>
                
                <div className="space-y-4">
                  {categories.slice(0, 5).map((cat, index) => {
                    const catMenPerc = cat.count > 0 ? Math.round((cat.men_count / cat.count) * 100) : 0;
                    const catWomenPerc = cat.count > 0 ? Math.round((cat.women_count / cat.count) * 100) : 0;
                    
                    return (
                      <div key={index} className="space-y-2" data-testid={`category-${index}`}>
                        <div className="flex justify-between items-baseline">
                          <div className="font-outfit font-medium">{cat.category}</div>
                          <div className="text-sm text-muted-foreground">{cat.count}</div>
                        </div>
                        <div className="flex gap-1 h-2">
                          <div 
                            className="bg-man"
                            style={{ width: `${catMenPerc}%` }}
                          />
                          <div 
                            className="bg-woman"
                            style={{ width: `${catWomenPerc}%` }}
                          />
                        </div>
                        <div className="flex gap-4 text-xs font-outfit">
                          <span style={{ color: '#002FA7' }}>{catMenPerc}% Men</span>
                          <span style={{ color: '#FF4500' }}>{catWomenPerc}% Women</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {stats.milestones && stats.milestones.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.35 }}
                className="brutalist-card bg-card p-8"
                data-testid="milestones-card"
              >
                <div className="flex items-center gap-2 mb-6">
                  <Trophy size={24} weight="bold" />
                  <h3 className="font-syne font-bold text-2xl">MILESTONES</h3>
                </div>
                
                <div className="space-y-4">
                  {milestones.slice(0, 5).map((milestone, index) => {
                    const menPerc = milestone.men_at_milestone + milestone.women_at_milestone > 0 
                      ? Math.round((milestone.men_at_milestone / (milestone.men_at_milestone + milestone.women_at_milestone)) * 100)
                      : 0;
                    const womenPerc = 100 - menPerc;
                    
                    return (
                      <div key={index} className="space-y-2 p-4 border-2 border-current rounded-none" data-testid={`milestone-${index}`}>
                        <div className="flex justify-between items-baseline">
                          <div className="font-syne font-bold text-2xl" style={{ color: '#FFA500' }}>
                            {milestone.count.toLocaleString()}
                          </div>
                          <div className="text-xs font-outfit text-muted-foreground">
                            {new Date(milestone.achieved_at).toLocaleDateString()}
                          </div>
                        </div>
                        <div className="flex gap-1 h-2">
                          <div 
                            className="bg-man"
                            style={{ width: `${menPerc}%` }}
                          />
                          <div 
                            className="bg-woman"
                            style={{ width: `${womenPerc}%` }}
                          />
                        </div>
                        <div className="flex gap-4 text-xs font-outfit">
                          <span style={{ color: '#002FA7' }}>{milestone.men_at_milestone} Men</span>
                          <span style={{ color: '#FF4500' }}>{milestone.women_at_milestone} Women</span>
                        </div>
                      </div>
                    );
                  })}
                  
                  {stats.total_queries > 0 && (
                    <div className="pt-4 border-t-2 border-current">
                      <div className="text-sm font-outfit text-muted-foreground">
                        Next milestone: <span className="font-bold">{(Math.floor(stats.total_queries / 100000) + 1) * 100000}</span>
                      </div>
                      <div className="mt-2 h-2 bg-muted rounded-none overflow-hidden">
                        <div 
                          className="h-full bg-foreground"
                          style={{ 
                            width: `${((stats.total_queries % 100000) / 100000) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {recentQueries.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="brutalist-card bg-card p-8"
            data-testid="recent-queries-card"
          >
            <h3 className="font-syne font-bold text-2xl mb-6">RECENT QUERIES</h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
              {recentQueries.map((query, index) => (
                <div 
                  key={query.id} 
                  className="p-4 border-2 border-current rounded-none"
                  data-testid={`recent-query-${index}`}
                >
                  <div 
                    className="w-2 h-2 rounded-none mb-2"
                    style={{
                      backgroundColor: query.result === 'man' ? '#002FA7' : query.result === 'woman' ? '#FF4500' : '#808080'
                    }}
                  />
                  <div className="font-outfit font-medium text-sm truncate">{query.input_text}</div>
                  <div className="text-xs text-muted-foreground mt-1">{query.creator_name}</div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default App;