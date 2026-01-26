from django import template

register = template.Library()

@register.simple_tag
def get_step_class(current_status, step_name):
    # Define the strict order of your progress steps
    status_order = ['New', 'Accepted', 'On_the_way', 'Completed']
    
    try:
        # Find where the order currently is (e.g., index 2)
        current_index = status_order.index(current_status)
        
        # Find where this specific dot is (e.g., index 1)
        step_index = status_order.index(step_name)
        
        # If the order has passed this step, return 'active' class
        if current_index >= step_index:
            return 'active'
    except ValueError:
        # If status is 'Cancelled' or unknown, return nothing
        return ''
    
    return ''