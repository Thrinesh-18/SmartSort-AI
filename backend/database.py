"""
SmartSort-AI Database Module
Handles storage for classification history and recycling facilities
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import math

class Database:
    """
    SQLite database handler for PlasticNet
    """
    
    def __init__(self, db_path='plasticnet.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
    
    def initialize(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Classification history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plastic_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                image_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Recycling facilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT NOT NULL,
                accepts_pet BOOLEAN DEFAULT 1,
                accepts_hdpe BOOLEAN DEFAULT 1,
                accepts_other BOOLEAN DEFAULT 0,
                phone TEXT,
                hours TEXT,
                website TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                classification_id INTEGER,
                correct_prediction BOOLEAN,
                actual_type TEXT,
                comments TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (classification_id) REFERENCES classification_history(id)
            )
        ''')
        
        self.conn.commit()
        
        # Add sample facilities if table is empty
        cursor.execute('SELECT COUNT(*) FROM facilities')
        if cursor.fetchone()[0] == 0:
            self._add_sample_facilities()
        
        print("✅ Database initialized")
    
    def _add_sample_facilities(self):
        """Add sample recycling facilities for demo"""
        sample_facilities = [
            {
                'name': 'EcoRecycle Center',
                'latitude': 12.9716,
                'longitude': 77.5946,
                'address': 'MG Road, Bengaluru, Karnataka 560001',
                'accepts_pet': True,
                'accepts_hdpe': True,
                'accepts_other': False,
                'phone': '+91-80-12345678',
                'hours': 'Mon-Sat: 9 AM - 6 PM',
                'website': 'https://ecorecycle.example.com'
            },
            {
                'name': 'Green Earth Recycling',
                'latitude': 12.9352,
                'longitude': 77.6245,
                'address': 'Indiranagar, Bengaluru, Karnataka 560038',
                'accepts_pet': True,
                'accepts_hdpe': True,
                'accepts_other': True,
                'phone': '+91-80-98765432',
                'hours': 'Mon-Sun: 8 AM - 8 PM',
                'website': 'https://greenearth.example.com'
            },
            {
                'name': 'City Waste Management',
                'latitude': 12.9160,
                'longitude': 77.6101,
                'address': 'Koramangala, Bengaluru, Karnataka 560034',
                'accepts_pet': True,
                'accepts_hdpe': False,
                'accepts_other': False,
                'phone': '+91-80-55555555',
                'hours': 'Mon-Fri: 10 AM - 5 PM',
                'website': None
            }
        ]
        
        for facility in sample_facilities:
            self.add_facility(**facility)
        
        print("✅ Added sample recycling facilities")
    
    def add_classification_history(self, plastic_type: str, confidence: float, image_name: Optional[str] = None):
        """
        Record a classification attempt
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO classification_history (plastic_type, confidence, image_name)
            VALUES (?, ?, ?)
        ''', (plastic_type, confidence, image_name))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_classification_history(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Get classification history with pagination
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, plastic_type, confidence, image_name, timestamp
            FROM classification_history
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def delete_history_record(self, record_id: int) -> bool:
        """
        Delete a classification history record
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM classification_history WHERE id = ?', (record_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def add_facility(self, name: str, latitude: float, longitude: float, address: str,
                    accepts_pet: bool = True, accepts_hdpe: bool = True, accepts_other: bool = False,
                    phone: Optional[str] = None, hours: Optional[str] = None, 
                    website: Optional[str] = None):
        """
        Add a new recycling facility
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO facilities 
            (name, latitude, longitude, address, accepts_pet, accepts_hdpe, accepts_other, phone, hours, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, latitude, longitude, address, accepts_pet, accepts_hdpe, accepts_other, phone, hours, website))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_nearby_facilities(self, latitude: float, longitude: float, 
                             plastic_type: Optional[str] = None, 
                             radius_km: float = 10.0) -> List[Dict]:
        """
        Find nearby recycling facilities within radius
        Uses Haversine formula for distance calculation
        """
        cursor = self.conn.cursor()
        
        # Build query based on plastic type filter
        query = '''
            SELECT id, name, latitude, longitude, address, 
                   accepts_pet, accepts_hdpe, accepts_other,
                   phone, hours, website
            FROM facilities
            WHERE 1=1
        '''
        params = []
        
        # Filter by accepted plastic types
        if plastic_type:
            plastic_type = plastic_type.upper()
            if plastic_type == 'PET':
                query += ' AND accepts_pet = 1'
            elif plastic_type == 'HDPE':
                query += ' AND accepts_hdpe = 1'
            elif plastic_type == 'OTHER':
                query += ' AND accepts_other = 1'
        
        cursor.execute(query, params)
        facilities = cursor.fetchall()
        
        # Calculate distances and filter by radius
        nearby = []
        for facility in facilities:
            facility_dict = dict(facility)
            distance = self._calculate_distance(
                latitude, longitude,
                facility_dict['latitude'], facility_dict['longitude']
            )
            
            if distance <= radius_km:
                facility_dict['distance_km'] = round(distance, 2)
                facility_dict['accepts_types'] = []
                
                if facility_dict['accepts_pet']:
                    facility_dict['accepts_types'].append('PET')
                if facility_dict['accepts_hdpe']:
                    facility_dict['accepts_types'].append('HDPE')
                if facility_dict['accepts_other']:
                    facility_dict['accepts_types'].append('OTHER')
                
                nearby.append(facility_dict)
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        
        return nearby
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def get_statistics(self) -> Dict:
        """
        Get system statistics
        """
        cursor = self.conn.cursor()
        
        # Total classifications
        cursor.execute('SELECT COUNT(*) FROM classification_history')
        total_classifications = cursor.fetchone()[0]
        
        # Classifications by type
        cursor.execute('''
            SELECT plastic_type, COUNT(*) as count
            FROM classification_history
            GROUP BY plastic_type
        ''')
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average confidence
        cursor.execute('SELECT AVG(confidence) FROM classification_history')
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Total facilities
        cursor.execute('SELECT COUNT(*) FROM facilities')
        total_facilities = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM classification_history
            WHERE timestamp >= datetime('now', '-1 day')
        ''')
        recent_activity = cursor.fetchone()[0]
        
        return {
            'total_classifications': total_classifications,
            'classifications_by_type': by_type,
            'average_confidence': round(avg_confidence, 4),
            'total_facilities': total_facilities,
            'recent_activity_24h': recent_activity
        }
    
    def add_feedback(self, classification_id: int, correct_prediction: bool, 
                    actual_type: Optional[str] = None, comments: Optional[str] = None):
        """
        Add user feedback for a classification
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (classification_id, correct_prediction, actual_type, comments)
            VALUES (?, ?, ?, ?)
        ''', (classification_id, correct_prediction, actual_type, comments))
        self.conn.commit()
        return cursor.lastrowid
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")


# ============================================
# TESTING
# ============================================

if __name__ == '__main__':
    print("🧪 Testing Database Module...\n")
    
    db = Database('test_plasticnet.db')
    db.initialize()
    
    # Test adding classification
    print("Adding classification history...")
    id1 = db.add_classification_history('PET', 0.95, 'bottle1.jpg')
    print(f"✅ Added record ID: {id1}")
    
    # Test getting history
    print("\nGetting history...")
    history = db.get_classification_history(limit=10)
    print(f"✅ Found {len(history)} records")
    
    # Test nearby facilities
    print("\nSearching for nearby facilities...")
    facilities = db.get_nearby_facilities(12.9716, 77.5946, 'PET', radius_km=20)
    print(f"✅ Found {len(facilities)} facilities")
    for f in facilities:
        print(f"  - {f['name']}: {f['distance_km']} km away")
    
    # Test statistics
    print("\nGetting statistics...")
    stats = db.get_statistics()
    print(f"✅ Statistics: {stats}")
    
    db.close()
    print("\n🎉 Database module test complete!")