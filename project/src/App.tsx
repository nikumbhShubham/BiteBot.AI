import React, { useState } from 'react';
import { ChefHat, TrendingUp, MapPin, MessageCircle, Sparkles,  Github, } from 'lucide-react';
import FoodAgent from './components/FoodAgent';
import DealAgent from './components/DealAgent';
import ChatInterface from './components/ChatInterface';

function App() {
  const [activeTab, setActiveTab] = useState('food');
  const [location, setLocation] = useState('Mumbai');
  const [isLoading, setIsLoading] = useState(false);

  const tabs = [
    { id: 'food', label: 'Food Recommendations', icon: ChefHat },
    { id: 'deals', label: 'Smart Deals', icon: TrendingUp },
    { id: 'chat', label: 'Food Chat', icon: MessageCircle }
  ];
  

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-red-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-red-500 to-red-600 p-2 rounded-xl shadow-lg">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-red-600 to-red-700 bg-clip-text text-transparent">
                  BiteBot
                </h1>
                <p className="text-sm text-gray-600">Your smart eating buddy.</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-white rounded-full px-4 py-2 shadow-sm border border-red-100">
                <MapPin className="h-4 w-4 text-red-500" />
                <select 
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="bg-transparent text-sm font-medium text-gray-700 focus:outline-none"
                >
                  <option value="Mumbai">Mumbai</option>
                  <option value="Delhi">Delhi</option>
                  <option value="Bangalore">Bangalore</option>
                  <option value="Chennai">Chennai</option>
                  <option value="Kolkata">Kolkata</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="flex space-x-1 bg-white/60 backdrop-blur-sm rounded-2xl p-1 shadow-lg border border-red-100">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg shadow-red-200 transform scale-105'
                    : 'text-gray-600 hover:text-red-600 hover:bg-red-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="transition-all duration-500 ease-in-out">
          {activeTab === 'food' && <FoodAgent location={location} />}
          {activeTab === 'deals' && <DealAgent location={location} />}
          {activeTab === 'chat' && <ChatInterface location={location} />}
        </div>
      </main>

      {/* Footer */}
       <footer className="bg-white/80 backdrop-blur-sm border-t border-red-100 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-center space-x-3 text-gray-600">
            <h2 className="text-sm font-medium">Developed By: Shubham Nikumbh</h2>
            <a
              href="https://github.com/nikumbhShubham/BiteBot.AI"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-red-600"
              title="View on GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;