import { useState } from "react";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import { Badge } from "./ui/badge";
import { 
  Home, 
  TrendingUp, 
  PieChart, 
  Eye, 
  Bell, 
  Settings, 
  Search, 
  Plus,
  BarChart3,
  DollarSign,
  Globe,
  Newspaper,
  Calculator,
  Target,
  Star,
  ChevronRight,
  User,
  LogOut
} from "lucide-react";

interface PortfolioSidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  onLogout: () => void;
}

export function PortfolioSidebar({ currentPage, onNavigate, onLogout }: PortfolioSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const mainNavItems = [
    { id: 'main-portfolio', label: 'My Portfolio', icon: Home, badge: null },
    { id: 'stocks', label: 'Stocks', icon: TrendingUp, badge: '9' },
    { id: 'mutual-funds', label: 'Mutual Funds', icon: PieChart, badge: '14' },
    { id: 'watchlist', label: 'Watchlist', icon: Eye, badge: '23' },
    { id: 'markets', label: 'Markets', icon: BarChart3, badge: null },
    { id: 'news', label: 'News', icon: Newspaper, badge: null },
  ];

  const toolsItems = [
    { id: 'screener', label: 'Stock Screener', icon: Search },
    { id: 'calculator', label: 'Calculator', icon: Calculator },
    { id: 'research', label: 'Research', icon: Target },
    { id: 'alerts', label: 'Alerts', icon: Bell },
  ];

  const quickStats = [
    { label: 'Portfolio Value', value: '$186,543', change: '+2.4%', positive: true },
    { label: 'Day\'s Gain/Loss', value: '+$4,329', change: '+2.4%', positive: true },
    { label: 'Total Gain/Loss', value: '+$18,654', change: '+11.1%', positive: true },
  ];

  return (
    <div className={`${isCollapsed ? 'w-16' : 'w-64'} bg-gray-900/95 backdrop-blur-md border-r border-gray-700/50 h-full flex flex-col transition-all duration-300`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700/50">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"></div>
              <span className="text-lg bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Portfolio Hub</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="text-gray-400 hover:text-white hover:bg-gray-800"
          >
            <ChevronRight className={`h-4 w-4 transition-transform ${isCollapsed ? '' : 'rotate-180'}`} />
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      {!isCollapsed && (
        <div className="p-4 border-b border-gray-700/50">
          <h3 className="text-sm text-gray-400 mb-3">Portfolio Overview</h3>
          <div className="space-y-3">
            {quickStats.map((stat, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-xs text-gray-400">{stat.label}</span>
                <div className="text-right">
                  <div className="text-sm text-white">{stat.value}</div>
                  <div className={`text-xs ${stat.positive ? 'text-green-400' : 'text-red-400'}`}>
                    {stat.change}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Navigation */}
      <div className="flex-1 p-4 space-y-1">
        <div className="space-y-1">
          {mainNavItems.map((item) => {
            const IconComponent = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <Button
                key={item.id}
                variant="ghost"
                className={`w-full justify-start ${isActive ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'} ${isCollapsed ? 'px-2' : ''}`}
                onClick={() => onNavigate(item.id)}
              >
                <IconComponent className={`h-4 w-4 ${isCollapsed ? '' : 'mr-3'}`} />
                {!isCollapsed && (
                  <>
                    <span className="flex-1 text-left">{item.label}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="bg-gray-700 text-gray-300 text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </>
                )}
              </Button>
            );
          })}
        </div>

        {!isCollapsed && (
          <>
            <Separator className="my-4 bg-gray-700" />
            
            {/* Tools Section */}
            <div className="space-y-1">
              <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-2">Tools</h3>
              {toolsItems.map((item) => {
                const IconComponent = item.icon;
                
                return (
                  <Button
                    key={item.id}
                    variant="ghost"
                    className="w-full justify-start text-gray-400 hover:text-white hover:bg-gray-800"
                    onClick={() => onNavigate(item.id)}
                  >
                    <IconComponent className="h-4 w-4 mr-3" />
                    <span>{item.label}</span>
                  </Button>
                );
              })}
            </div>

            <Separator className="my-4 bg-gray-700" />

            {/* Quick Actions */}
            <div className="space-y-2">
              <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-2">Quick Actions</h3>
              <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 border-0">
                <Plus className="h-4 w-4 mr-2" />
                Add Investment
              </Button>
              <Button variant="outline" className="w-full border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white">
                <Star className="h-4 w-4 mr-2" />
                Add to Watchlist
              </Button>
            </div>
          </>
        )}
      </div>

      {/* User Section */}
      <div className="p-4 border-t border-gray-700/50">
        {!isCollapsed ? (
          <div className="space-y-2">
            <Button
              variant="ghost"
              className="w-full justify-start text-gray-400 hover:text-white hover:bg-gray-800"
              onClick={() => onNavigate('settings')}
            >
              <User className="h-4 w-4 mr-3" />
              <span>Account</span>
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-gray-400 hover:text-white hover:bg-gray-800"
              onClick={() => onNavigate('settings')}
            >
              <Settings className="h-4 w-4 mr-3" />
              <span>Settings</span>
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-gray-400 hover:text-red-400 hover:bg-gray-800"
              onClick={onLogout}
            >
              <LogOut className="h-4 w-4 mr-3" />
              <span>Sign Out</span>
            </Button>
          </div>
        ) : (
          <div className="space-y-1">
            <Button
              variant="ghost"
              size="sm"
              className="w-full text-gray-400 hover:text-white hover:bg-gray-800"
              onClick={() => onNavigate('settings')}
            >
              <Settings className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="w-full text-gray-400 hover:text-red-400 hover:bg-gray-800"
              onClick={onLogout}
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}