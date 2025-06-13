import React, { useState, useEffect } from 'react';
import { 
  Percent, 
  Clock, 
  TrendingDown, 
  AlertCircle, 
  Store, 
  Star,
  Timer,
  Zap,
  Target,
  Loader2,
  Sparkles,
  Filter,
  X
} from 'lucide-react';

interface DealAgentProps {
  location: string;
}

interface Deal {
  restaurant: string;
  deal: string;
  type: string;
  urgency: string;
  original_price?: number;
  discounted_price?: number;
  rationale?: string;
  cuisine?: string;
  rating?: number;
  expires_in?: string;
}

interface ApiResponse {
  deals: Deal[];
  marketing_ideas?: string[];
  total_savings: number;
  high_priority_count: number;
  average_rating: number;
  timestamp?: string;
  error?: string;
}

const API_BASE_URL = 'http://localhost:5000'; // Change in production

const DealAgent: React.FC<DealAgentProps> = ({ location }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [totalSavings, setTotalSavings] = useState(0);
  const [highPriorityCount, setHighPriorityCount] = useState(0);
  const [averageRating, setAverageRating] = useState(0);
  const [activeFilters, setActiveFilters] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const fetchDeals = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/deals/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          location: location
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setDeals(data.deals || []);
      setTotalSavings(data.total_savings || 0);
      setHighPriorityCount(data.high_priority_count || 0);
      setAverageRating(data.average_rating || 0);
      setLastUpdated(data.timestamp || new Date().toISOString());
      
    } catch (err) {
      console.error('Error fetching deals:', err);
      setError(err instanceof Error ? err.message : 'Failed to load deals');
      // Fallback to mock data if API fails
      setDeals(getMockDeals());
      calculateMockStats();
    } finally {
      setIsLoading(false);
    }
  };

  // Mock data fallback
  const getMockDeals = (): Deal[] => [
    {
      restaurant: 'Tandoori Tales',
      deal: '30% off Paneer Tikka',
      type: 'clearance',
      urgency: 'high',
      original_price: 150,
      discounted_price: 105,
      rationale: 'Low stock needs clearing before closing',
      cuisine: 'Indian',
      rating: 4.0,
      expires_in: '2 hours'
    },
    // ... (other mock deals)
        {
      restaurant: 'Dragon Bowl',
      deal: '25% off all menu',
      type: 'slow_sales',
      urgency: 'medium',
      rationale: 'Boost evening sales with attractive discounts',
      cuisine: 'Chinese',
      rating: 4.3,
      expires_in: '4 hours'
    },
    {
      restaurant: 'Pizza & Co.',
      deal: '40% off Pepperoni Pizza',
      type: 'closing_soon',
      urgency: 'high',
      original_price: 220,
      discounted_price: 132,
      rationale: 'Restaurant closing in 2 hours, clear inventory',
      cuisine: 'Italian',
      rating: 4.4,
      expires_in: '2 hours'
    },
    {
      restaurant: 'Chaat Corner',
      deal: 'Buy 2 Get 1 Free Pani Puri',
      type: 'innovative',
      urgency: 'medium',
      rationale: 'High demand item, boost customer satisfaction',
      cuisine: 'Street Food',
      rating: 4.2,
      expires_in: '3 hours'
    },
    {
      restaurant: 'Bento Box',
      deal: '35% off Sushi Rolls',
      type: 'clearance',
      urgency: 'high',
      original_price: 200,
      discounted_price: 130,
      rationale: 'Premium ingredients need to be used today',
      cuisine: 'Japanese',
      rating: 4.7,
      expires_in: '1 hour'
    }
  ];

  const calculateMockStats = () => {
    const mockDeals = getMockDeals();
    const savings = mockDeals.reduce((total, deal) => {
      if (deal.original_price && deal.discounted_price) {
        return total + (deal.original_price - deal.discounted_price);
      }
      return total;
    }, 0);
    
    setTotalSavings(savings);
    setHighPriorityCount(mockDeals.filter(d => d.urgency === 'high').length);
    setAverageRating(
      mockDeals.reduce((sum, d) => sum + (d.rating || 0), 0) / mockDeals.length
    );
  };

  useEffect(() => {
    fetchDeals();
  }, [location]);

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'clearance': return <TrendingDown className="h-4 w-4" />;
      case 'closing_soon': return <Clock className="h-4 w-4" />;
      case 'slow_sales': return <Target className="h-4 w-4" />;
      case 'innovative': return <Sparkles className="h-4 w-4" />;
      default: return <Percent className="h-4 w-4" />;
    }
  };

  const filterOptions = [
    { value: 'high', label: 'High Urgency' },
    { value: 'medium', label: 'Medium Urgency' },
    { value: 'clearance', label: 'Clearance' },
    { value: 'closing_soon', label: 'Closing Soon' },
    { value: 'innovative', label: 'Innovative' }
  ];

  const filteredDeals = deals.filter(deal => {
    if (activeFilters.length === 0) return true;
    return activeFilters.includes(deal.urgency) || activeFilters.includes(deal.type);
  });

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-8">
      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            <span>{error}</span>
          </div>
          <p className="text-sm mt-2">Showing sample data. Please check your connection.</p>
        </div>
      )}

      {/* Last Updated */}
      {lastUpdated && (
        <div className="text-sm text-gray-500 text-right">
          Last updated: {formatTime(lastUpdated)}
        </div>
      )}

      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Active Deals Card */}
        <StatCard 
          icon={<Store className="h-8 w-8 text-red-500" />}
          title="Active Deals"
          value={deals.length.toString()}
          description="Available right now"
        />

        {/* Potential Savings Card */}
        <StatCard 
          icon={<Percent className="h-8 w-8 text-green-500" />}
          title="Potential Savings"
          value={`₹${totalSavings}`}
          description="Total possible savings"
          valueColor="text-green-600"
        />

        {/* High Priority Card */}
        <StatCard 
          icon={<AlertCircle className="h-8 w-8 text-red-500" />}
          title="High Priority"
          value={highPriorityCount.toString()}
          description="Urgent deals"
          valueColor="text-red-600"
        />

        {/* Avg Rating Card */}
        <StatCard 
          icon={<Star className="h-8 w-8 text-yellow-500" />}
          title="Avg Rating"
          value={averageRating.toFixed(1)}
          description="Average restaurant rating"
          valueColor="text-yellow-600"
        />
      </div>

      {/* Action Button */}
      <div className="flex justify-center">
        <button
          onClick={fetchDeals}
          disabled={isLoading}
          className="bg-gradient-to-r from-red-500 to-red-600 text-white px-8 py-4 rounded-2xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-3"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Zap className="h-5 w-5" />
          )}
          <span>{isLoading ? 'Analyzing Deals...' : 'Refresh Smart Deals'}</span>
        </button>
      </div>

      {/* Filters */}
      <FilterSection 
        filters={filterOptions}
        activeFilters={activeFilters}
        onFilterToggle={(filter) => 
          setActiveFilters(prev => 
            prev.includes(filter) 
              ? prev.filter(f => f !== filter)
              : [...prev, filter]
          )
        }
        onClearFilters={() => setActiveFilters([])}
      />

      {/* Deals Grid */}
      {filteredDeals.length > 0 ? (
        <DealsGrid 
          deals={filteredDeals}
          getUrgencyColor={getUrgencyColor}
          getTypeIcon={getTypeIcon}
        />
      ) : (
        <NoResults 
          isLoading={isLoading}
          hasDeals={deals.length > 0}
          onResetFilters={() => setActiveFilters([])}
        />
      )}
    </div>
  );
};

// Component Breakdown:

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  description: string;
  valueColor?: string;
}

const StatCard: React.FC<StatCardProps> = ({ 
  icon, 
  title, 
  value, 
  description,
  valueColor = 'text-gray-900'
}) => (
  <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100 hover:shadow-xl transition-all duration-300">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className={`text-2xl font-bold ${valueColor}`}>{value}</p>
        <p className="text-xs text-gray-500 mt-1">{description}</p>
      </div>
      {icon}
    </div>
  </div>
);

interface FilterSectionProps {
  filters: { value: string; label: string }[];
  activeFilters: string[];
  onFilterToggle: (filter: string) => void;
  onClearFilters: () => void;
}

const FilterSection: React.FC<FilterSectionProps> = ({
  filters,
  activeFilters,
  onFilterToggle,
  onClearFilters
}) => (
  <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100">
    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
      <Filter className="h-5 w-5 mr-2 text-red-500" />
      Filter Deals
    </h3>
    <div className="flex flex-wrap gap-3">
      {filters.map((filter) => (
        <button
          key={filter.value}
          onClick={() => onFilterToggle(filter.value)}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 flex items-center ${
            activeFilters.includes(filter.value)
              ? 'bg-red-500 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 hover:bg-red-100 hover:text-red-700'
          }`}
        >
          {filter.label}
        </button>
      ))}
      {activeFilters.length > 0 && (
        <button
          onClick={onClearFilters}
          className="px-4 py-2 rounded-xl text-sm font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 transition-all duration-300 flex items-center"
        >
          <X className="h-4 w-4 mr-1" />
          Clear All
        </button>
      )}
    </div>
  </div>
);

interface DealsGridProps {
  deals: Deal[];
  getUrgencyColor: (urgency: string) => string;
  getTypeIcon: (type: string) => React.ReactNode;
}

const DealsGrid: React.FC<DealsGridProps> = ({ deals, getUrgencyColor, getTypeIcon }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-3">
      <Percent className="h-6 w-6 text-red-500" />
      <span>Smart Deal Recommendations</span>
    </h2>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {deals.map((deal, index) => (
        <DealCard 
          key={index}
          deal={deal}
          getUrgencyColor={getUrgencyColor}
          getTypeIcon={getTypeIcon}
        />
      ))}
    </div>
  </div>
);

interface DealCardProps {
  deal: Deal;
  getUrgencyColor: (urgency: string) => string;
  getTypeIcon: (type: string) => React.ReactNode;
}

const DealCard: React.FC<DealCardProps> = ({ deal, getUrgencyColor, getTypeIcon }) => (
  <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-red-100 hover:shadow-xl transform hover:scale-[1.02] transition-all duration-300 relative overflow-hidden">
    {/* Urgency Badge */}
    <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold border ${getUrgencyColor(deal.urgency)}`}>
      {deal.urgency.toUpperCase()}
    </div>

    {/* Header */}
    <div className="flex items-start justify-between mb-4 pr-20">
      <div>
        <h3 className="text-lg font-bold text-gray-900">{deal.restaurant}</h3>
        <div className="flex items-center space-x-2 mt-1">
          <span className="text-sm text-gray-600 capitalize">{deal.cuisine}</span>
          {deal.rating && (
            <div className="flex items-center space-x-1">
              <Star className="h-3 w-3 text-yellow-500 fill-current" />
              <span className="text-sm text-gray-600">{deal.rating}</span>
            </div>
          )}
        </div>
      </div>
    </div>

    {/* Deal Info */}
    <div className="mb-4">
      <div className="flex items-center space-x-2 mb-2">
        {getTypeIcon(deal.type)}
        <span className="text-xl font-bold text-red-600">{deal.deal}</span>
      </div>
      
      {deal.original_price && deal.discounted_price && (
        <div className="flex items-center space-x-3">
          <span className="text-lg font-bold text-green-600">₹{deal.discounted_price}</span>
          <span className="text-sm text-gray-500 line-through">₹{deal.original_price}</span>
          <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">
            Save ₹{deal.original_price - deal.discounted_price}
          </span>
        </div>
      )}
    </div>

    {/* Rationale */}
    {deal.rationale && (
      <p className="text-sm text-gray-700 mb-4 bg-blue-50 p-3 rounded-xl border border-blue-100">
        💡 {deal.rationale}
      </p>
    )}

    {/* Footer */}
    <div className="flex items-center justify-between pt-4 border-t border-gray-200">
      <div className="flex items-center space-x-2 text-sm text-gray-600">
        <Timer className="h-4 w-4 text-red-500" />
        <span>Expires in {deal.expires_in || 'soon'}</span>
      </div>
      <button className="bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-2 rounded-xl text-sm font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-300">
        Claim Deal
      </button>
    </div>
  </div>
);

interface NoResultsProps {
  isLoading: boolean;
  hasDeals: boolean;
  onResetFilters: () => void;
}

const NoResults: React.FC<NoResultsProps> = ({ isLoading, hasDeals, onResetFilters }) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-red-100">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-red-200 border-t-red-500"></div>
            <p className="text-gray-600 font-medium">Analyzing restaurant data...</p>
            <p className="text-sm text-gray-500">Finding the best deals for you</p>
          </div>
        </div>
      </div>
    );
  }

  if (!hasDeals) {
    return (
      <div className="text-center py-12">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-red-100 max-w-md mx-auto">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-700">No deals available</h3>
          <p className="text-sm text-gray-500 mt-2">
            There are currently no deals in your area. Please check back later.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="text-center py-12">
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-red-100 max-w-md mx-auto">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-700">No matching deals</h3>
        <p className="text-sm text-gray-500 mt-2">
          Your filters didn't match any deals. Try adjusting your filters.
        </p>
        <button
          onClick={onResetFilters}
          className="mt-4 bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-600 transition-colors"
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
};

export default DealAgent;