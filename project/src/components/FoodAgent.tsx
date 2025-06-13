import React, { useState, useEffect } from 'react';
import { 
  CloudRain, 
  Sun, 
  Thermometer, 
  Calendar,  // Added Calendar icon
  TrendingUp, 
  Clock,
  Sparkles,
  MapPin,
  // ChefHat,
  Star,
  Tag,
  Loader2,
  PartyPopper  // Added for festivals
} from 'lucide-react';

interface FoodAgentProps {
  location: string;
}

interface WeatherData {
  condition: string;
  description: string;
  temperature: number;
  humidity: number;
  food_suggestions: string[];
  city?: string;
}

interface Festival {
  name: string;
  date_range?: string;
  foods?: string[];
  popular_orders?: string[];
  significance?: string;
}

interface Recommendation {
  dish_name: string;
  cuisine: string;
  reason: string;
  explanation?: string;
  confidence: number;
  tags: string[];
  price_range: string;
  meal_type: string;
}

interface ApiResponse {
  recommendations: Recommendation[];
  context: {
    weather: WeatherData;
    location: string;
    festivals?: {
      festivals: Festival[];
    };
    current_month?: string;
  };
  errors?: string[];
  demo_mode?: boolean;
}

const API_BASE_URL = 'http://localhost:5000';

const FoodAgent: React.FC<FoodAgentProps> = ({ location }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [festivals, setFestivals] = useState<Festival[]>([]);
  const [currentMonth, setCurrentMonth] = useState<string>('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [errors, setErrors] = useState<string[]>([]);
  const [demoMode, setDemoMode] = useState(false);

  const fetchRecommendations = async () => {
    setIsLoading(true);
    setErrors([]);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/food/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'react_user',
          location: location
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      
      setRecommendations(data.recommendations || []);
      setWeatherData(data.context?.weather || null);
      setFestivals(data.context?.festivals?.festivals || []);
      setCurrentMonth(data.context?.current_month || '');
      setDemoMode(data.demo_mode || false);
      
      if (data.errors && data.errors.length > 0) {
        setErrors(data.errors);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setErrors([`Failed to load recommendations: ${error.message}`]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [location]);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'rain':
        return <CloudRain className="h-5 w-5 text-blue-500" />;
      case 'clear':
        return <Sun className="h-5 w-5 text-yellow-500" />;
      case 'clouds':
        return <CloudRain className="h-5 w-5 text-gray-500" />;
      case 'snow':
        return <CloudRain className="h-5 w-5 text-blue-200" />;
      default:
        return <Sun className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getPriceRangeColor = (range: string) => {
    switch (range.toLowerCase()) {
      case 'budget':
        return 'bg-green-100 text-green-700';
      case 'mid':
        return 'bg-yellow-100 text-yellow-700';
      case 'premium':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getMealTypeIcon = (mealType: string) => {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return '🌅';
      case 'lunch':
        return '🍽️';
      case 'dinner':
        return '🌙';
      case 'snack':
        return '🍪';
      default:
        return '🍴';
    }
  };

  return (
    <div className="space-y-8">
      {/* Demo Mode Notice */}
      {demoMode && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded-lg">
          <p className="font-medium">Demo Mode Active</p>
          <p className="text-sm">
            Using sample data. For full features, please configure API keys in the backend.
          </p>
        </div>
      )}

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-lg">
          <p className="font-medium">Notice</p>
          <ul className="list-disc list-inside text-sm">
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Header Stats - Updated with Festival Info */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100 hover:shadow-xl transition-all duration-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Location</p>
              <p className="text-xl font-bold text-gray-900">
                {weatherData?.city || location}
              </p>
            </div>
            <MapPin className="h-8 w-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100 hover:shadow-xl transition-all duration-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Weather</p>
              <p className="text-xl font-bold text-gray-900">
                {weatherData?.temperature || '--'}°C
              </p>
              {weatherData?.description && (
                <p className="text-xs text-gray-500 capitalize">{weatherData.description}</p>
              )}
            </div>
            {weatherData && getWeatherIcon(weatherData.condition)}
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100 hover:shadow-xl transition-all duration-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Time</p>
              <p className="text-xl font-bold text-gray-900">
                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
              {currentMonth && (
                <p className="text-xs text-gray-500">{currentMonth}</p>
              )}
            </div>
            <Clock className="h-8 w-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100 hover:shadow-xl transition-all duration-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Festivals</p>
              <p className="text-xl font-bold text-gray-900">
                {festivals.length > 0 ? festivals.length : 'None'}
              </p>
              {festivals.length > 0 && (
                <p className="text-xs text-gray-500">This month</p>
              )}
            </div>
            <PartyPopper className="h-8 w-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="flex justify-center">
        <button
          onClick={fetchRecommendations}
          disabled={isLoading}
          className="bg-gradient-to-r from-red-500 to-red-600 text-white px-8 py-4 rounded-2xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-3"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Sparkles className="h-5 w-5" />
          )}
          <span>{isLoading ? 'Getting Recommendations...' : 'Get Smart Recommendations'}</span>
        </button>
      </div>

      {/* Weather Insights */}
      {weatherData?.food_suggestions && weatherData.food_suggestions.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-2xl p-6 shadow-lg border border-blue-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Thermometer className="h-5 w-5 text-blue-500" />
            <span>Weather-Based Suggestions</span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {weatherData.food_suggestions.map((suggestion, index) => (
              <div key={index} className="bg-white/80 backdrop-blur-sm rounded-xl p-3 text-center">
                <span className="text-sm font-medium text-gray-700 capitalize">{suggestion}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Festival Insights - New Section */}
      {festivals.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-2xl p-6 shadow-lg border border-purple-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <PartyPopper className="h-5 w-5 text-purple-500" />
            <span>Festival Specials ({currentMonth})</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {festivals.map((festival, index) => (
              <div key={index} className="bg-white/80 backdrop-blur-sm rounded-xl p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-bold text-gray-900">{festival.name}</h4>
                  {festival.date_range && (
                    <span className="flex items-center text-xs text-gray-500">
                      <Calendar className="h-3 w-3 mr-1" />
                      {festival.date_range}
                    </span>
                  )}
                </div>
                
                {festival.significance && (
                  <p className="text-sm text-gray-600 mb-3">{festival.significance}</p>
                )}
                
                {festival.foods && festival.foods.length > 0 && (
                  <div className="mb-2">
                    <p className="text-xs font-medium text-gray-500 mb-1">Traditional Foods:</p>
                    <div className="flex flex-wrap gap-2">
                      {festival.foods.map((food, foodIndex) => (
                        <span 
                          key={foodIndex} 
                          className="inline-block bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full capitalize"
                        >
                          {food}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {festival.popular_orders && festival.popular_orders.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">Popular Orders:</p>
                    <div className="flex flex-wrap gap-2">
                      {festival.popular_orders.map((order, orderIndex) => (
                        <span 
                          key={orderIndex} 
                          className="inline-block bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full capitalize"
                        >
                          {order}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations Grid */}
      {recommendations.length > 0 && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-3">
            <TrendingUp className="h-6 w-6 text-red-500" />
            <span>Personalized Recommendations</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recommendations.map((rec, index) => (
              <div
                key={index}
                className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100 hover:shadow-xl transform hover:scale-[1.02] transition-all duration-300"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{rec.dish_name}</h3>
                    <p className="text-sm text-gray-600 capitalize">{rec.cuisine}</p>
                  </div>
                  <div className="flex items-center space-x-1 bg-yellow-100 px-2 py-1 rounded-full">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <span className="text-xs font-medium text-yellow-700">
                      {Math.round(rec.confidence * 100)}%
                    </span>
                  </div>
                </div>

                <p className="text-gray-700 mb-4 text-sm leading-relaxed">
                  {rec.explanation || rec.reason}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-2">
                    {rec.tags.slice(0, 3).map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700 capitalize"
                      >
                        <Tag className="h-3 w-3 mr-1" />
                        {tag}
                      </span>
                    ))}
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriceRangeColor(rec.price_range)} capitalize`}>
                    {rec.price_range}
                  </span>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 flex items-center">
                      {getMealTypeIcon(rec.meal_type)}&nbsp;
                      <span className="capitalize">Best for {rec.meal_type}</span>
                    </span>
                    <button className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-300">
                      Order Now
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-red-100">
            <div className="flex flex-col items-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-red-200 border-t-red-500"></div>
              <p className="text-gray-600 font-medium">Analyzing your preferences...</p>
              <p className="text-sm text-gray-500">Considering weather, trends, and local favorites</p>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && recommendations.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-red-100 text-center max-w-md">
            <h3 className="text-lg font-bold text-gray-900 mb-2">No Recommendations Found</h3>
            <p className="text-gray-600 mb-4">
              We couldn't find any recommendations for your location. Try again or check back later.
            </p>
            <button
              onClick={fetchRecommendations}
              className="bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-2 rounded-xl font-medium"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FoodAgent;