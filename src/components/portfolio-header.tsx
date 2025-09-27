import { Button } from "./ui/button";
import { MoreHorizontal, RefreshCw, Download, Settings } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu";

export function PortfolioHeader() {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl">Portfolio Dashboard</h1>
        <p className="text-muted-foreground">
          Track your stocks and mutual funds performance
        </p>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
        
        <Button variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem>Add New Holding</DropdownMenuItem>
            <DropdownMenuItem>View Performance Reports</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}