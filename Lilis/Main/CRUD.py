class CRUD:
    def get(self, id):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def list(self):
        return self.model.objects.all()

    def delete(self, id):
        try:
            instance = self.model.objects.get(id=id)
            instance.delete()
            return True
        except self.model.DoesNotExist:
            return False

    def save(self, data):
        form = self.form_class(data)
        if form.is_valid():
            obj = form.save()
            return True, obj
        return False, form

    def update(self, id, data):
        try:
            instance = self.model.objects.get(id=id)
            form = self.form_class(data, instance=instance)
            if form.is_valid():
                form.save()
                return True, form
            return False, form
        except self.model.DoesNotExist:
            return False, None
        
    def search_by_name(self, name):
        return self.model.objects.filter(name__icontains=name)
    
    def count(self):
        return self.model.objects.count()
