"""
3D GitHub Contributions Visualizer

This program creates a 3D visualization of GitHub contributions for a year.
You can either fetch real data from GitHub or use sample data for demonstration.

Requirements:
    pip install matplotlib numpy requests beautifulsoup4 --break-system-packages

Usage:
    python github_contributions_3d.py
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re


def fetch_github_contributions(username, year=None):
    """
    Fetch GitHub contribution data for a specific user and year.
    
    Args:
        username (str): GitHub username
        year (int): Year to fetch data for (defaults to current year)
    
    Returns:
        dict: Dictionary with dates as keys and contribution counts as values
    """
    if year is None:
        year = datetime.now().year
    
    url = f"https://github.com/{username}"
    
    try:
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find contribution data in the SVG graph
        contributions = {}
        
        # Look for contribution rects in the SVG
        svg = soup.find('svg', class_='js-calendar-graph-svg')
        if svg:
            for rect in svg.find_all('rect', class_='ContributionCalendar-day'):
                date_str = rect.get('data-date')
                count_str = rect.get('data-level', '0')
                
                if date_str:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    if date_obj.year == year:
                        # Estimate contribution count based on level (0-4)
                        # GitHub uses levels, we'll map them to approximate counts
                        level = int(count_str) if count_str.isdigit() else 0
                        count = level * 5  # Approximate mapping
                        contributions[date_str] = count
        
        if contributions:
            print(f"Successfully fetched {len(contributions)} days of contribution data for {username}")
            return contributions
        else:
            print(f"Could not fetch contribution data for {username}. Using sample data instead.")
            return None
            
    except Exception as e:
        print(f"Error fetching GitHub data: {e}")
        print("Using sample data instead.")
        return None


def generate_sample_data(year=None):
    """
    Generate sample contribution data for demonstration.
    
    Args:
        year (int): Year to generate data for
    
    Returns:
        dict: Dictionary with dates as keys and contribution counts as values
    """
    if year is None:
        year = datetime.now().year
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    contributions = {}
    current_date = start_date
    
    while current_date <= end_date:
        # Generate realistic-looking contribution patterns
        day_of_week = current_date.weekday()
        
        # Less activity on weekends
        if day_of_week >= 5:  # Saturday or Sunday
            base_contributions = np.random.poisson(2)
        else:
            base_contributions = np.random.poisson(8)
        
        # Add some variability
        contributions[current_date.strftime('%Y-%m-%d')] = max(0, base_contributions)
        current_date += timedelta(days=1)
    
    return contributions


def prepare_grid_data(contributions):
    """
    Convert contribution dictionary to a grid format (weeks x days).
    
    Args:
        contributions (dict): Dictionary with dates and contribution counts
    
    Returns:
        tuple: (grid array, weeks, days, dates)
    """
    # Sort dates
    dates = sorted(contributions.keys())
    start_date = datetime.strptime(dates[0], '%Y-%m-%d')
    
    # Calculate starting Sunday
    days_to_sunday = (start_date.weekday() + 1) % 7
    grid_start = start_date - timedelta(days=days_to_sunday)
    
    # Create grid (52-53 weeks x 7 days)
    weeks = 53
    days = 7
    grid = np.zeros((weeks, days))
    date_grid = [[None for _ in range(days)] for _ in range(weeks)]
    
    for date_str, count in contributions.items():
        date = datetime.strptime(date_str, '%Y-%m-%d')
        days_diff = (date - grid_start).days
        
        if days_diff >= 0:
            week = days_diff // 7
            day = days_diff % 7
            
            if week < weeks:
                grid[week, day] = count
                date_grid[week][day] = date_str
    
    return grid, weeks, days, date_grid


def create_3d_visualization(grid, username="GitHub User", year=None):
    """
    Create a 3D bar chart visualization of GitHub contributions.
    
    Args:
        grid (numpy.array): Grid of contribution counts
        username (str): GitHub username for the title
        year (int): Year being visualized
    """
    weeks, days = grid.shape
    
    # Create figure and 3D axis
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create meshgrid for bar positions
    x_pos, y_pos = np.meshgrid(range(weeks), range(days))
    x_pos = x_pos.flatten()
    y_pos = y_pos.flatten()
    z_pos = np.zeros_like(x_pos)
    
    # Flatten the grid for heights
    dz = grid.T.flatten()
    
    # Bar dimensions
    dx = dy = 0.8
    
    # Create color map based on contribution intensity
    colors = plt.cm.Greens(dz / (dz.max() + 1))
    
    # Create 3D bars
    ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, 
             color=colors, edgecolor='gray', linewidth=0.5, alpha=0.9)
    
    # Customize the plot
    ax.set_xlabel('Week of Year', fontsize=12, labelpad=10)
    ax.set_ylabel('Day of Week', fontsize=12, labelpad=10)
    ax.set_zlabel('Contributions', fontsize=12, labelpad=10)
    
    # Set y-axis labels to day names
    day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    ax.set_yticks(range(7))
    ax.set_yticklabels(day_names)
    
    # Set x-axis to show every 4th week
    ax.set_xticks(range(0, weeks, 4))
    ax.set_xticklabels([f'W{i}' for i in range(0, weeks, 4)])
    
    # Title
    year_str = f" ({year})" if year else ""
    title = f"GitHub Contributions - {username}{year_str}"
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Adjust viewing angle
    ax.view_init(elev=25, azim=45)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add statistics text
    total_contributions = int(np.sum(dz))
    max_contributions = int(np.max(dz))
    avg_contributions = np.mean(dz[dz > 0]) if np.any(dz > 0) else 0
    
    stats_text = f"Total: {total_contributions} | Max: {max_contributions} | Avg: {avg_contributions:.1f}"
    fig.text(0.5, 0.02, stats_text, ha='center', fontsize=12, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig


def save_visualization(fig, filename='github_contributions_3d.png'):
    """Save the visualization to a file."""
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {filename}")


def main():
    """Main function to run the visualization."""
    print("=" * 60)
    print("GitHub Contributions 3D Visualizer")
    print("=" * 60)
    
    # Get user input
    use_real_data = input("\nFetch real GitHub data? (y/n, default=n): ").strip().lower()
    
    if use_real_data == 'y':
        username = input("Enter GitHub username: ").strip()
        year_input = input("Enter year (default=current year): ").strip()
        year = int(year_input) if year_input else datetime.now().year
        
        print(f"\nFetching data for {username} ({year})...")
        contributions = fetch_github_contributions(username, year)
        
        if contributions is None:
            print("Falling back to sample data...")
            contributions = generate_sample_data(year)
            username = "Sample User"
    else:
        year_input = input("Enter year for sample data (default=current year): ").strip()
        year = int(year_input) if year_input else datetime.now().year
        
        print(f"\nGenerating sample data for {year}...")
        contributions = generate_sample_data(year)
        username = "Sample User"
    
    # Prepare grid data
    print("Preparing visualization...")
    grid, weeks, days, date_grid = prepare_grid_data(contributions)
    
    # Create visualization
    print("Creating 3D visualization...")
    fig = create_3d_visualization(grid, username, year)
    
    # Save option
    save_option = input("\nSave visualization to file? (y/n, default=y): ").strip().lower()
    if save_option != 'n':
        filename = input("Enter filename (default=github_contributions_3d.png): ").strip()
        if not filename:
            filename = 'github_contributions_3d.png'
        save_visualization(fig, filename)
    
    # Display
    print("\nDisplaying visualization...")
    plt.show()
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
