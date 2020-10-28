class Rectangle:
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.x = x
        self.y = y




class QuadtreeNode:
    def __init__(self, l, rec = Rectangle(0,0,0,0)):
        self.max_objects = 10
        self.max_levels = 5
        self.level = l
        self.objects = []
        self.rectangle_properties = rec
        self.children = []
        
        

    def clear(self):
        self.objects = None
        for node in self.children:
            node.clear()
            node = None

    def split(self):
        subWidth =  self.rectangle_properties.width /2
        subHeight = self.rectangle_properties.height /2
        x = self.rectangle_properties.x
        y = self.rectangle_properties.y
        
        rectangle_top_right = Rectangle(x, y, subWidth, subHeight)
        rectangle_top_left = Rectangle(x + subWidth, y, subWidth, subHeight)
        rectangle_down_right = Rectangle(x, y + subHeight, subWidth, subHeight)
        rectangle_down_left = Rectangle(x + subWidth, y + subHeight, subWidth, subHeight)
        new_level = self.level + 1
        children_to_be = []

        children_to_be.append( QuadtreeNode(new_level, rectangle_top_right) )
        children_to_be.append( QuadtreeNode(new_level, rectangle_top_left) )
        children_to_be.append( QuadtreeNode(new_level, rectangle_down_right) )
        children_to_be.append( QuadtreeNode(new_level, rectangle_down_left) )
        return children_to_be


    # Determine which node the object belongs to. -1 means
    # object cannot completely fit within a child node and is part
    # of the parent node
    def getIndex (self, p_rect):
        index = -1
        vertical_midpoint = self.rectangle_properties.x + self.rectangle_properties.width/2
        horizontal_midpoint = self.rectangle_properties.y + self.rectangle_properties.height/2

        # Object can completely fit within the top quadrants
        is_top_quadrant = ( (p_rect.x < horizontal_midpoint) and ((p_rect.y +p_rect.height) < horizontal_midpoint) )
        # Object can completely fit within the bottom quadrants
        is_bottom_quadrant = p_rect.y > horizontal_midpoint

        # Object can completely fit within the left quadrants
        if ( p_rect.x < vertical_midpoint and ((p_rect.x +p_rect.width) < vertical_midpoint) ):
            if is_top_quadrant:
                index = 1
            elif is_bottom_quadrant:
                index = 2
        # Object can completely fit within the right quadrantsObject can completely fit within the right quadrants
        elif p_rect.x > vertical_midpoint:
            if is_top_quadrant:
                index = 0
            elif is_bottom_quadrant:
                index = 3

        return index

 

    # Insert the object into the quadtree. If the node
    # exceeds the capacity, it will split and add all
    # objects to their corresponding nodes.
    def insert(self, p_rect):
        children = self.children

        if children[0] is not None:
            index = self.getIndex(p_rect)
            if (index != -1):
                self.children[index].insert(p_rect)
                return

        self.objects.append(p_rect)

        if self.objects.count > self.max_objects and self.level < self.max_levels:
            if self.children[0] is not None:
                self.split()

        i = 0
        while i< self.objects.count:            
            index = self.getIndex( self.objects[i] )
            if (index != -1):
                self.children[index].insert(self.objects.remove(i))
            else:
                i = i + 1


    # Return all objects that could collide with the given object
    def retrieve(self, returnObjects, p_rect):
        index = self.getIndex(p_rect)

        if index != -1 and self.children[0] is not None:
            self.children[index].retrieve(returnObjects,p_rect)
        
        returnObjects.extend(self.objects)
        
        return returnObjects
