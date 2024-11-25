static bool match_exception_partial(struct list_head *exceptions, short type,
				    u32 major, u32 minor, short access)
{
	struct dev_exception_item *ex;

	list_for_each_entry_rcu(ex, exceptions, list,
				lockdep_is_held(&devcgroup_mutex)) {
		if ((type & DEVCG_DEV_BLOCK) && !(ex->type & DEVCG_DEV_BLOCK))
			continue;
		if ((type & DEVCG_DEV_CHAR) && !(ex->type & DEVCG_DEV_CHAR))
			continue;
		/*
		 * We must be sure that both the exception and the provided
		 * range aren't masking all devices
		 */
		if (ex->major != ~0 && major != ~0 && ex->major != major)
			continue;
		if (ex->minor != ~0 && minor != ~0 && ex->minor != minor)
			continue;
		/*
		 * In order to make sure the provided range isn't matching
		 * an exception, all its access bits shouldn't match the
		 * exception's access bits
		 */
		if (!(access & ex->access))
			continue;
		return true;
	}
	return false;
}